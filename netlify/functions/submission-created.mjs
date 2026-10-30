// Сповіщення в Telegram про кожну нову заявку з форм сайту (замовлення, безкоштовна розмальовка, відгук…).
// Netlify сам викликає цю функцію після кожної перевіреної заявки Netlify Forms (назва файлу — це подія).
// У Netlify → Project configuration → Environment variables потрібні:
//   TELEGRAM_BOT_TOKEN — токен бота від @BotFather
//   TELEGRAM_CHAT_ID   — id чату, куди слати сповіщення (необовʼязково, за замовчуванням — Telegram власника)
// Без токена функція нічого не робить, а заявки, як і раніше, зберігаються в Netlify Forms.

const TITLES = {
  order: '🛒 Нове замовлення',
  free: '🎁 Безкоштовна «Блискавка 95»',
  'free-sheet': '🎁 Безкоштовний аркуш',
  review: '⭐ Новий відгук',
  preorder: '📝 Передзамовлення',
};

const esc = (s) => String(s ?? '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

function message(form, d) {
  const lines = [`<b>${TITLES[form] || `📩 Заявка: ${esc(form)}`}</b>`];
  if (form === 'order') {
    if (d.product) lines.push(`Товар: ${esc(d.product)}`);
    if (d.price) lines.push(`Сума: ${esc(d.price)} ₴`);
    if (d.code) lines.push(`Код оплати: <code>${esc(d.code)}</code>`);
    lines.push('', 'Перевірте оплату в банці monobank і надішліть PDF.');
  } else if (form === 'review') {
    if (d.name) lines.push(`Імʼя: ${esc(d.name)}`);
    if (d.stars) lines.push(`Оцінка: ${'★'.repeat(+d.stars || 0)}`);
    if (d.text) lines.push(`«${esc(String(d.text).slice(0, 500))}»`);
    if (d.photo) lines.push('Є фото');
  } else {
    for (const [k, v] of Object.entries(d)) {
      if (['email', 'agree', 'form-name', 'bot-field', 'ip', 'user_agent', 'referrer'].includes(k) || !v) continue;
      lines.push(`${esc(k)}: ${esc(typeof v === 'object' ? JSON.stringify(v) : v)}`);
    }
  }
  if (d.email) lines.push(`E-mail: ${esc(d.email)}`);
  return lines.join('\n');
}

export const handler = async (event) => {
  const token = process.env.TELEGRAM_BOT_TOKEN, chat = process.env.TELEGRAM_CHAT_ID || '514450638';
  if (!token || !chat) return { statusCode: 200 };

  let payload = {};
  try { ({ payload = {} } = JSON.parse(event.body || '{}')); } catch {}
  const form = payload.form_name || payload.data?.['form-name'] || 'form';

  const r = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      chat_id: chat,
      text: message(form, payload.data || {}),
      parse_mode: 'HTML',
      link_preview_options: { is_disabled: true },
    }),
  });
  if (!r.ok) console.error('Telegram', r.status, await r.text());
  return { statusCode: 200 };
};
