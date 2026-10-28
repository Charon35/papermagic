// Безкоштовна розмальовка за e-mail: одразу надсилає лист із PDF через Brevo.
// У Netlify → Project configuration → Environment variables потрібні:
//   BREVO_API_KEY — ключ API з Brevo (SMTP & API → API Keys)
//   SENDER_EMAIL  — підтверджена в Brevo адреса відправника (за замовчуванням papermagic.ua@gmail.com)
// Без ключа функція відповідає sent:false, а сайт однаково одразу показує кнопку завантаження.

const PDF_PATH = '/free/blyskavka-95.pdf';
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export default async (req) => {
  if (req.method !== 'POST') return new Response('Method not allowed', { status: 405 });

  let email = '';
  try { ({ email = '' } = await req.json()); } catch {}
  email = String(email).trim();
  if (!EMAIL_RE.test(email) || email.length > 200) return Response.json({ ok: false }, { status: 400 });

  const key = process.env.BREVO_API_KEY;
  if (!key) return Response.json({ ok: true, sent: false });

  const site = process.env.URL || 'https://jade-pegasus-1ae52b.netlify.app';
  const pdf = site + PDF_PATH;
  const html = `
    <div style="font-family:Arial,sans-serif;font-size:16px;line-height:1.5;color:#2a2440;max-width:520px">
      <h2 style="margin:0 0 12px">Ваша безкоштовна розмальовка 🏎</h2>
      <p>Дякуємо, що завітали до PaperMagic! У вкладенні — PDF гоночної машинки «Блискавка 95».</p>
      <p>Роздрукуйте на А4 → розмалюйте → виріжте → склейте 3D-фігурку. Друкувати можна скільки завгодно для своєї родини.</p>
      <p><a href="${pdf}" style="display:inline-block;background:#6a4cf0;color:#fff;text-decoration:none;font-weight:bold;padding:12px 22px;border-radius:999px">Завантажити PDF</a></p>
      <p>Сподобалось? Ще 12 фігурок і вигідні набори чекають на сайті: <a href="${site}">${site.replace('https://', '')}</a></p>
      <p style="color:#6b6580;font-size:14px">PaperMagic · Instagram @papermagic_ua</p>
    </div>`;

  const r = await fetch('https://api.brevo.com/v3/smtp/email', {
    method: 'POST',
    headers: { 'api-key': key, 'content-type': 'application/json', accept: 'application/json' },
    body: JSON.stringify({
      sender: { name: 'PaperMagic', email: process.env.SENDER_EMAIL || 'papermagic.ua@gmail.com' },
      to: [{ email }],
      subject: 'Ваша безкоштовна розмальовка «Блискавка 95» 🏎',
      htmlContent: html,
      attachment: [{ url: pdf, name: 'PaperMagic-Blyskavka-95.pdf' }],
    }),
  });
  if (!r.ok) console.error('Brevo', r.status, await r.text());
  return Response.json({ ok: true, sent: r.ok });
};

export const config = { path: '/api/free-sheet' };
