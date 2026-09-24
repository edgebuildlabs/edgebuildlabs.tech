// WhatsApp: o número mora só aqui. Para ligar, troque o marcador pelo número em formato internacional, só dígitos
// (55, DDD e número; sem +, espaço ou traço) e rode `npm run build`. A mensagem pronta de cada idioma mora no pt.json e
// no en.json (contato.itens, chave "whatsapp"); aqui ela vira URL-encoding.
export const NUMERO_WHATSAPP = 'NUMERO_WHATSAPP'

export const linkWhatsApp = (mensagem) => `https://wa.me/${NUMERO_WHATSAPP}?text=${encodeURIComponent(mensagem)}`

if (!/^\d+$/.test(NUMERO_WHATSAPP)) {
  console.warn(`[whatsapp] o número ainda é o marcador "${NUMERO_WHATSAPP}" (src/data/whatsapp.js): o link não abre conversa.`)
}
