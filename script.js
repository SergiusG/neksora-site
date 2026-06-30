// ===== Header scroll state =====
const header = document.querySelector('[data-header]');
const nav = document.querySelector('[data-nav]');
const navToggle = document.querySelector('[data-nav-toggle]');
const form = document.querySelector('[data-form]');
const formNote = document.querySelector('[data-form-note]');

const setHeaderState = () => {
  header?.classList.toggle('is-scrolled', window.scrollY > 16);
};
setHeaderState();
window.addEventListener('scroll', setHeaderState, { passive: true });

// ===== Mobile nav =====
navToggle?.addEventListener('click', () => {
  const isOpen = nav?.classList.toggle('is-open');
  document.body.classList.toggle('nav-open', Boolean(isOpen));
  navToggle.setAttribute('aria-expanded', String(Boolean(isOpen)));
});

nav?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    nav.classList.remove('is-open');
    document.body.classList.remove('nav-open');
    navToggle?.setAttribute('aria-expanded', 'false');
  });
});

// ===== Scroll reveal =====
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));

// ===== Form handling =====
form?.addEventListener('submit', (event) => {
  event.preventDefault();
  const requiredFields = form.querySelectorAll('[required]');
  let isValid = true;

  requiredFields.forEach((field) => {
    const invalid = !field.value.trim();
    field.classList.toggle('is-invalid', invalid);
    if (invalid) isValid = false;
  });

  if (!isValid) {
    formNote.textContent = 'Заполните обязательные поля: имя и телефон.';
    formNote.className = 'form-note error';
    return;
  }

  // Collect form data
  const data = new FormData(form);
  const name = data.get('name');
  const phone = data.get('phone');
  const object = data.get('object');
  const message = data.get('message');

  // TODO: Replace with real backend (Telegram bot / email / CRM)
  console.log('Form submission:', { name, phone, object, message });

  formNote.textContent = 'Спасибо! Заявка отправлена. Мы свяжемся с вами в ближайшее время.';
  formNote.className = 'form-note success';
  form.reset();

  // Clear success message after 5s
  setTimeout(() => {
    formNote.textContent = '';
    formNote.className = 'form-note';
  }, 5000);
});

// Clear invalid state on input
form?.querySelectorAll('input, select, textarea').forEach((field) => {
  field.addEventListener('input', () => field.classList.remove('is-invalid'));
  field.addEventListener('change', () => field.classList.remove('is-invalid'));
});

// ===== Smooth scroll for anchor links =====
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
