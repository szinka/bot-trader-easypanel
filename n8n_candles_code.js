// Código corrigido para n8n - Processamento de Candles
// Compatível com as correções do get_candles

const velas = $('HTTP Request11').first().json.velas;
if (!Array.isArray(velas) || velas.length === 0) {
  throw new Error("API não retornou uma lista de velas válida ou o caminho para os dados está incorreto.");
}

const candles = velas.map((vela) => {
  const timestamp = vela.from;
  const data = new Date(timestamp * 1000).toISOString().replace('T', ' ').substring(0, 19);

  // Mapeia os campos corretos baseado nas correções do get_candles
  const open = parseFloat(vela.open) || 0;
  const close = parseFloat(vela.close) || 0;
  const high = parseFloat(vela.high) || Math.max(open, close);
  const low = parseFloat(vela.low) || Math.min(open, close);
  const volume = parseFloat(vela.volume) || 0;

  // Validação adicional para garantir dados corretos
  const validatedHigh = Math.max(high, open, close);
  const validatedLow = Math.min(low, open, close);

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

// Log para debug (opcional)
console.log(`Processados ${candles.length} candles`);
if (candles.length > 0) {
  console.log('Exemplo de candle processado:', candles[0]);
}

return [{
  json: {
    candles: candles
  }
}]; 