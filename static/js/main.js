/* T&TG Trade Corp — Main JS */
document.addEventListener('DOMContentLoaded', function () {

  /* ── Navbar scroll shadow ── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.boxShadow = window.scrollY > 40 ? '0 4px 30px rgba(0,0,0,.5)' : 'none';
    });
  }

  /* ── Animate elements on scroll ── */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity .6s ease, transform .6s ease';
    observer.observe(el);
  });

  /* ── Live forex ticker ── */
  const fakeRates = [
    { sym: 'USD/CAD', rate: '1.3812', chg: '+0.12%', up: true },
    { sym: 'USD/UGX', rate: '3,720.00', chg: '+0.08%', up: true },
    { sym: 'EUR/USD', rate: '1.0934', chg: '-0.05%', up: false },
    { sym: 'GBP/USD', rate: '1.2711', chg: '+0.21%', up: true },
    { sym: 'USD/KES', rate: '129.45', chg: '-0.03%', up: false },
    { sym: 'USD/JPY', rate: '153.82', chg: '+0.31%', up: true },
    { sym: 'EUR/GBP', rate: '0.8601', chg: '-0.09%', up: false },
    { sym: 'BTC/USD', rate: '67,430', chg: '+1.24%', up: true },
  ];
  const tc = document.getElementById('tickerContent');
  if (tc) {
    tc.innerHTML = fakeRates.map(r =>
      `<span class="ticker-item"><span class="sym">${r.sym}</span><span class="prc">${r.rate}</span><span class="${r.up ? 'up' : 'dn'}">${r.chg}</span></span>`
    ).join('');
  }

  /* ── Avon Points calculator ── */
  const calcInputs = document.querySelectorAll('.avon-calc-input');
  calcInputs.forEach(inp => {
    inp.addEventListener('input', () => {
      const price = parseFloat(inp.dataset.price || inp.value) || 0;
      const qty = parseFloat(inp.dataset.qty || 1);
      const total = price * qty;
      const consumer = (total / 5.5).toFixed(2);
      const referral = (total / 8.5).toFixed(2);
      const outConsumer = document.getElementById('pts-consumer');
      const outReferral = document.getElementById('pts-referral');
      if (outConsumer) outConsumer.textContent = consumer;
      if (outReferral) outReferral.textContent = referral;
    });
  });

  /* ── Multi-step registration ── */
  let currentStep = 0;
  const steps = document.querySelectorAll('.reg-step');
  const stepDots = document.querySelectorAll('.si-item');
  function showStep(n) {
    steps.forEach((s, i) => {
      s.classList.toggle('active', i === n);
    });
    stepDots.forEach((d, i) => {
      d.classList.remove('active', 'done');
      if (i < n) d.classList.add('done');
      if (i === n) d.classList.add('active');
    });
    currentStep = n;
  }
  const nextBtns = document.querySelectorAll('.step-next');
  const prevBtns = document.querySelectorAll('.step-prev');
  nextBtns.forEach(b => b.addEventListener('click', () => {
    if (currentStep < steps.length - 1) showStep(currentStep + 1);
  }));
  prevBtns.forEach(b => b.addEventListener('click', () => {
    if (currentStep > 0) showStep(currentStep - 1);
  }));
  if (steps.length) showStep(0);

  /* ── Auto-dismiss alerts ── */
  document.querySelectorAll('.alert.auto-dismiss').forEach(a => {
    setTimeout(() => {
      a.style.transition = 'opacity .5s ease';
      a.style.opacity = '0';
      setTimeout(() => a.remove(), 500);
    }, 4000);
  });

  /* ── Market type toggle ── */
  const mktSelect = document.getElementById('id_market_type');
  const intlFields = document.getElementById('intl-only-fields');
  if (mktSelect && intlFields) {
    function toggleIntl() {
      intlFields.style.display = mktSelect.value === 'local' ? 'none' : 'block';
    }
    mktSelect.addEventListener('change', toggleIntl);
    toggleIntl();
  }

  /* ── Delivery type toggle ── */
  const deliverySelect = document.getElementById('id_delivery_type');
  const deliveryNote = document.getElementById('delivery-note');
  if (deliverySelect && deliveryNote) {
    deliverySelect.addEventListener('change', () => {
      if (deliverySelect.value === 'express') {
        deliveryNote.textContent = '⚡ Express delivery — higher shipping costs, fastest arrival.';
        deliveryNote.className = 'small text-warning mt-1';
      } else {
        deliveryNote.textContent = '🚢 Ordinary delivery — standard shipping costs.';
        deliveryNote.className = 'small text-info mt-1';
      }
    });
  }

  /* ── Order total live calc ── */
  const qtyInput = document.getElementById('id_quantity');
  const priceData = document.getElementById('product-price-data');
  if (qtyInput && priceData) {
    const unitPrice = parseFloat(priceData.dataset.price) || 0;
    qtyInput.addEventListener('input', () => {
      const qty = parseInt(qtyInput.value) || 1;
      const total = (unitPrice * qty).toFixed(2);
      const pts5 = (total / 5.5).toFixed(2);
      const pts8 = (total / 8.5).toFixed(2);
      const tOut = document.getElementById('order-total');
      const p5Out = document.getElementById('pts-5');
      const p8Out = document.getElementById('pts-8');
      if (tOut) tOut.textContent = '$' + parseFloat(total).toLocaleString();
      if (p5Out) p5Out.textContent = pts5;
      if (p8Out) p8Out.textContent = pts8;
    });
  }

  /* ── Country selector redirect ── */
  document.querySelectorAll('[data-country-redirect]').forEach(el => {
    el.addEventListener('click', () => {
      const country = el.dataset.countryRedirect;
      const url = el.dataset.url || `/marketplace/products/?country=${country}`;
      window.location.href = url;
    });
  });

  /* ── Copy profile link ── */
  const copyBtn = document.getElementById('copy-profile-link');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const link = copyBtn.dataset.link;
      navigator.clipboard.writeText(link).then(() => {
        const orig = copyBtn.textContent;
        copyBtn.textContent = '✓ Copied!';
        setTimeout(() => { copyBtn.textContent = orig; }, 2000);
      });
    });
  }

  /* ── Number counter animation ── */
  function animateCount(el) {
    const target = parseInt(el.dataset.count) || 0;
    let count = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      count = Math.min(count + step, target);
      el.textContent = count.toLocaleString() + (el.dataset.suffix || '');
      if (count >= target) clearInterval(timer);
    }, 25);
  }
  const countObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        animateCount(e.target);
        countObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('[data-count]').forEach(el => countObserver.observe(el));

  /* ── Tooltips ── */
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (typeof bootstrap !== 'undefined') {
    tooltipEls.forEach(el => new bootstrap.Tooltip(el));
  }

});
