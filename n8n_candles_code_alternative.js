// Código alternativo para n8n - Processamento de Candles com Fallbacks
// Versão robusta para diferentes estruturas de dados

const velas = $('HTTP Request11').first().json.velas;
if (!Array.isArray(velas) || velas.length === 0) {
  throw new Error("API não retornou uma lista de velas válida ou o caminho para os dados está incorreto.");
}

const candles = velas.map((vela, index) => {
  const timestamp = vela.from || vela.time || 0;
  const data = new Date(timestamp * 1000).toISOString().replace('T', ' ').substring(0, 19);

  // Mapeia campos com múltiplos fallbacks (como no get_candles)
  const open = parseFloat(vela.open || vela.open_price || 0);
  const close = parseFloat(vela.close || vela.close_price || 0);
  const high = parseFloat(vela.high || vela.max || vela.max_price || 0);
  const low = parseFloat(vela.low || vela.min || vela.min_price || 0);
  const volume = parseFloat(vela.volume || vela.vol || 0);

  // Validação e correção automática (como no get_candles)
  let validatedHigh = high;
  let validatedLow = low;

  // Se high e low são 0, usa open e close como fallback
  if (high === 0 && low === 0) {
    validatedHigh = Math.max(open, close);
    validatedLow = Math.min(open, close);
    console.log(`Candle ${index}: high/low zerados, usando open/close como fallback`);
  }

  // Garante que high >= max(open, close) e low <= min(open, close)
  const maxPrice = Math.max(open, close);
  const minPrice = Math.min(open, close);

  if (validatedHigh < maxPrice) {
    validatedHigh = maxPrice;
    console.log(`Candle ${index}: high ajustado para ${maxPrice}`);
  }

  if (validatedLow > minPrice) {
    validatedLow = minPrice;
    console.log(`Candle ${index}: low ajustado para ${minPrice}`);
  }

  return {
    data: data,
    abertura: open,
    fechamento: close,
    maxima: validatedHigh,
    minima: validatedLow,
    volume: volume
  };
});

// Ordena do mais antigo para o mais recente
candles.sort((a, b) => new Date(a.data) - new Date(b.data));

// Log para debug
console.log(`Processados ${candles.length} candles`);
if (candles.length > 0) {
  console.log('Exemplo de candle processado:', candles[0]);
  console.log('Estrutura original do primeiro candle:', velas[0]);
}

return [{
  json: {
    candles: candles
  }
}]; 