import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useEmpresas } from '../hooks/useEmpresas';
import * as api from '../api/client';
import { showToast } from '../components/layout/Toast';
import { CalculatorIcon, DocumentCheckIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const NumberInput = ({ label, value, onChange, isNegative = false, isPercentage = false }) => (
  <div className="flex justify-between items-center py-2 border-b border-sire-secondary/50">
    <span className="text-sm font-medium text-gray-300">{label}</span>
    <div className="flex items-center space-x-2">
      {isNegative && <span className="text-red-400 font-bold">-</span>}
      <input
        type="number"
        step="0.01"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-32 bg-sire-dark border border-sire-secondary rounded px-2 py-1 text-right text-sm text-white focus:outline-none focus:ring-1 focus:ring-sire-blue"
      />
      {isPercentage && <span className="text-gray-400 text-sm">%</span>}
    </div>
  </div>
);

const ResultRow = ({ label, value, isNegativeAllowed = true, highlight = false }) => {
  const isNegative = value < 0;
  const displayValue = Math.abs(value);
  const colorClass = highlight 
    ? 'text-sire-blue font-bold text-lg' 
    : isNegativeAllowed && isNegative 
      ? 'text-red-400 font-medium' 
      : 'text-white font-medium';

  return (
    <div className={`flex justify-between items-center py-2 ${highlight ? 'mt-4 pt-4 border-t-2 border-sire-blue' : 'border-b border-sire-secondary/50'}`}>
      <span className={`text-sm ${highlight ? 'font-bold text-white uppercase' : 'font-medium text-gray-300'}`}>{label}</span>
      <span className={colorClass}>
        {isNegativeAllowed && isNegative ? '-' : ''}
        {displayValue.toLocaleString('es-PE', { style: 'currency', currency: 'PEN' })}
      </span>
    </div>
  );
};

const CalculadoraImpuestosPage = () => {
  const { empresas, loading: empresasLoading } = useEmpresas();
  
  const [empresaId, setEmpresaId] = useState('');
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [anio, setAnio] = useState(new Date().getFullYear());
  
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [saving, setSaving] = useState(false);

  // Editable fields
  const [comprasNoGravadas, setComprasNoGravadas] = useState(0);
  const [creditoFiscalAnterior, setCreditoFiscalAnterior] = useState(0);
  const [percepciones, setPercepciones] = useState(0);
  const [tasaRenta, setTasaRenta] = useState(0.0100);
  const [saldoFavorRentaAnterior, setSaldoFavorRentaAnterior] = useState(0);

  const meses = [
    { value: 1, label: 'Enero' }, { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' }, { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' }, { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' }, { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' }, { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' }, { value: 12, label: 'Diciembre' }
  ];

  const anios = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  const handleCargar = async () => {
    if (!empresaId || !mes || !anio) {
      showToast.error('Seleccione empresa, mes y año');
      return;
    }
    setLoading(true);
    try {
      const response = await api.getCalculadoraImpuestos(empresaId, anio, mes);
      const result = response.data;
      
      setData(result);
      
      if (result.liquidacion) {
        setComprasNoGravadas(result.liquidacion.compras_no_gravadas || 0);
        setCreditoFiscalAnterior(result.liquidacion.credito_fiscal_anterior || 0);
        setPercepciones(result.liquidacion.percepciones || 0);
        setTasaRenta(result.liquidacion.tasa_renta || 0.0100);
        setSaldoFavorRentaAnterior(result.liquidacion.saldo_favor_renta_anterior || 0);
      } else {
        setComprasNoGravadas(0);
        setCreditoFiscalAnterior(0);
        setPercepciones(0);
        setTasaRenta(0.0100);
        setSaldoFavorRentaAnterior(0);
      }
      showToast.success('Datos cargados correctamente');
    } catch (error) {
      showToast.error('Error al cargar datos de impuestos');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!data) return;
    setSaving(true);
    try {
      const payload = {
        empresa: empresaId,
        anio: parseInt(anio, 10),
        mes: parseInt(mes, 10),
        compras_no_gravadas: parseFloat(comprasNoGravadas || 0),
        credito_fiscal_anterior: parseFloat(creditoFiscalAnterior || 0),
        percepciones: parseFloat(percepciones || 0),
        tasa_renta: parseFloat(tasaRenta || 0),
        saldo_favor_renta_anterior: parseFloat(saldoFavorRentaAnterior || 0),
      };
      await api.saveLiquidacionImpuesto(payload);
      showToast.success('Liquidación guardada correctamente');
    } catch (error) {
      showToast.error('Error al guardar liquidación');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const calc = useMemo(() => {
    if (!data?.totales_sire) return null;
    const totales = data.totales_sire;

    const ventasMonto = parseFloat(totales.ventas_monto || 0);
    const ventasIgv = parseFloat(totales.ventas_igv || 0);
    
    const comprasMonto = parseFloat(totales.compras_monto || 0);
    const comprasIgv = parseFloat(totales.compras_igv || 0);

    const cNoGravadas = parseFloat(comprasNoGravadas || 0);
    const cfAnterior = parseFloat(creditoFiscalAnterior || 0);
    const percep = parseFloat(percepciones || 0);
    const tRenta = parseFloat(tasaRenta || 0);
    const sfRenta = parseFloat(saldoFavorRentaAnterior || 0);

    // IGV
    const importeAPagarIgv = ventasIgv - comprasIgv;
    const saldoXPagar1 = importeAPagarIgv - cfAnterior;
    const saldoXPagarFinalIgv = saldoXPagar1 - percep;

    // Renta
    const renta = ventasMonto * tRenta;
    const saldoXPagarRenta = renta - sfRenta;

    // Total a pagar sum - only positives or true sum? Excel usually sums up the final liabilities
    const totalAPagar = saldoXPagarFinalIgv + saldoXPagarRenta; 

    return {
      ventasMonto, ventasIgv,
      comprasMonto, comprasIgv,
      cNoGravadas, cfAnterior, percep, tRenta, sfRenta,
      importeAPagarIgv, saldoXPagar1, saldoXPagarFinalIgv,
      renta, saldoXPagarRenta,
      totalAPagar
    };
  }, [data, comprasNoGravadas, creditoFiscalAnterior, percepciones, tasaRenta, saldoFavorRentaAnterior]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-3 mb-8"
      >
        <div className="p-3 bg-gradient-to-br from-sire-blue to-purple-600 rounded-xl shadow-lg">
          <CalculatorIcon className="h-8 w-8 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">Calculadora de Impuestos</h1>
          <p className="text-gray-400 mt-1">Liquidación mensual de IGV y Renta</p>
        </div>
      </motion.div>

      {/* Control Panel */}
      <div className="bg-sire-card border border-sire-secondary rounded-xl p-6 mb-8 shadow-xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Empresa</label>
            <select
              value={empresaId}
              onChange={(e) => setEmpresaId(e.target.value)}
              className="w-full bg-sire-dark border border-sire-secondary rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-sire-blue focus:ring-1 focus:ring-sire-blue transition-colors"
            >
              <option value="">Seleccione una empresa...</option>
              {empresas.map(emp => (
                <option key={emp.id} value={emp.id}>{emp.razon_social} ({emp.ruc})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Mes</label>
            <select
              value={mes}
              onChange={(e) => setMes(e.target.value)}
              className="w-full bg-sire-dark border border-sire-secondary rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-sire-blue transition-colors"
            >
              {meses.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Año</label>
            <select
              value={anio}
              onChange={(e) => setAnio(e.target.value)}
              className="w-full bg-sire-dark border border-sire-secondary rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-sire-blue transition-colors"
            >
              {anios.map(a => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
          <div>
            <button
              onClick={handleCargar}
              disabled={loading}
              className="w-full bg-sire-blue hover:bg-blue-600 text-white font-medium py-2.5 px-4 rounded-lg flex items-center justify-center space-x-2 transition-all shadow-lg shadow-blue-500/20 disabled:opacity-70"
            >
              {loading ? (
                <ArrowPathIcon className="h-5 w-5 animate-spin" />
              ) : (
                <CalculatorIcon className="h-5 w-5" />
              )}
              <span>{loading ? 'Cargando...' : 'Cargar Datos'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Calculator Grid */}
      {calc && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-8"
        >
          {/* LEFT: IGV */}
          <div className="bg-sire-card border border-sire-secondary rounded-xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-sire-blue to-purple-500"></div>
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <span className="bg-sire-blue/20 text-sire-blue p-2 rounded-lg mr-3">
                1
              </span>
              IMPUESTO GRAL. A LAS VENTAS
            </h2>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-bold text-gray-500 uppercase pb-2">
                <span>Concepto</span>
                <div className="flex space-x-8 w-48 justify-end">
                  <span>Monto</span>
                  <span>IGV</span>
                </div>
              </div>

              {/* Ventas */}
              <div className="flex justify-between items-center py-2 border-b border-sire-secondary/50">
                <span className="text-sm font-medium text-gray-300">VENTAS</span>
                <div className="flex space-x-4 w-48 justify-end text-sm text-white">
                  <span>{calc.ventasMonto.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</span>
                  <span className="font-medium text-sire-blue">{calc.ventasIgv.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</span>
                </div>
              </div>

              {/* Compras */}
              <div className="flex justify-between items-center py-2 border-b border-sire-secondary/50">
                <span className="text-sm font-medium text-gray-300">COMPRAS CON EL 18%</span>
                <div className="flex space-x-4 w-48 justify-end text-sm">
                  <span className="text-white">{calc.comprasMonto.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</span>
                  <span className="font-medium text-red-400">-{calc.comprasIgv.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</span>
                </div>
              </div>

              <NumberInput 
                label="COMPRAS NO GRAV." 
                value={comprasNoGravadas} 
                onChange={setComprasNoGravadas} 
              />

              <ResultRow label="IMPORTE A PAGAR" value={calc.importeAPagarIgv} />

              <NumberInput 
                label="CREDITO FISCAL ANTERIOR" 
                value={creditoFiscalAnterior} 
                onChange={setCreditoFiscalAnterior}
                isNegative 
              />

              <ResultRow label="SALDO X PAGAR 1" value={calc.saldoXPagar1} />

              <NumberInput 
                label="COMPROB. PERCEPC." 
                value={percepciones} 
                onChange={setPercepciones}
                isNegative 
              />

              <ResultRow 
                label="SALDO X PAGAR FINAL IGV" 
                value={calc.saldoXPagarFinalIgv} 
                highlight 
              />
            </div>
          </div>

          {/* RIGHT: RENTA & TOTAL */}
          <div className="space-y-8">
            <div className="bg-sire-card border border-sire-secondary rounded-xl p-6 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-sire-green to-emerald-500"></div>
              <h2 className="text-xl font-bold text-white mb-6 flex items-center">
                <span className="bg-sire-green/20 text-sire-green p-2 rounded-lg mr-3">
                  2
                </span>
                IMPUESTO A LA RENTA
              </h2>

              <div className="space-y-2">
                <div className="flex justify-between items-center py-2 border-b border-sire-secondary/50">
                  <span className="text-sm font-medium text-gray-300">VENTAS</span>
                  <span className="text-sm text-white">{calc.ventasMonto.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</span>
                </div>

                <NumberInput 
                  label="TASA" 
                  value={tasaRenta} 
                  onChange={setTasaRenta}
                />

                <ResultRow label="RENTA" value={calc.renta} isNegativeAllowed={false} />

                <NumberInput 
                  label="SALDO A FAVOR RENTA ANT." 
                  value={saldoFavorRentaAnterior} 
                  onChange={setSaldoFavorRentaAnterior}
                  isNegative 
                />

                <ResultRow 
                  label="SALDO X PAGAR RENTA" 
                  value={calc.saldoXPagarRenta} 
                  highlight 
                />
              </div>
            </div>

            {/* TOTAL */}
            <div className="bg-gradient-to-br from-sire-dark to-sire-card border border-sire-blue/30 rounded-xl p-6 shadow-2xl shadow-sire-blue/10">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-300">TOTAL A PAGAR</h3>
                <span className="text-3xl font-black bg-gradient-to-r from-sire-blue to-purple-400 bg-clip-text text-transparent">
                  {calc.totalAPagar.toLocaleString('es-PE', { style: 'currency', currency: 'PEN' })}
                </span>
              </div>
              
              <button
                onClick={handleSave}
                disabled={saving}
                className="w-full bg-gradient-to-r from-sire-green to-emerald-600 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-70"
              >
                {saving ? (
                  <ArrowPathIcon className="h-6 w-6 animate-spin" />
                ) : (
                  <DocumentCheckIcon className="h-6 w-6" />
                )}
                <span>{saving ? 'Guardando...' : 'Guardar Liquidación'}</span>
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default CalculadoraImpuestosPage;
