// Wait for DOM to be fully ready
document.addEventListener('DOMContentLoaded', function () {

  // ===== TYPEWRITER for EliteStore brand =====
  const brandElite = document.querySelector('.brand-elite');
  const brandStore = document.querySelector('.brand-store');
  if (brandElite && brandStore) {
    const eliteText = 'Elite';
    const storeText = 'Store';
    brandElite.textContent = '';
    brandStore.textContent = '';
    let i = 0, j = 0;
    function typeElite() {
      if (i < eliteText.length) {
        brandElite.textContent += eliteText[i++];
        setTimeout(typeElite, 90);
      } else {
        typeStore();
      }
    }
    function typeStore() {
      if (j < storeText.length) {
        brandStore.textContent += storeText[j++];
        setTimeout(typeStore, 90);
      }
    }
    setTimeout(typeElite, 300);
  }


  // Hamburger menu
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  if (hamburger) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      hamburger.classList.toggle('active');
    });
  }

  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.getElementById('mainNav');
    if (nav) nav.classList.toggle('scrolled', window.scrollY > 20);
  });

  // Counter animation
  function animateCounters() {
    document.querySelectorAll('[data-count]').forEach(el => {
      if (el.dataset.animated) return;
      el.dataset.animated = true;
      const target = parseInt(el.getAttribute('data-count'));
      let current = 0;
      const step = Math.ceil(target / 50);
      const timer = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current.toLocaleString();
        if (current >= target) clearInterval(timer);
      }, 25);
    });
  }

  // Intersection Observer — fires for ALL elements including those already in viewport
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
        if (e.target.hasAttribute('data-count') || e.target.querySelector('[data-count]')) {
          animateCounters();
        }
      }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px -20px 0px' });

  // Observe all animated elements
  document.querySelectorAll('.animate-on-scroll, [data-count]').forEach(el => {
    observer.observe(el);
  });

  // Force-trigger elements already visible in viewport (fix for fast loads)
  setTimeout(() => {
    document.querySelectorAll('.animate-on-scroll:not(.visible)').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        el.classList.add('visible');
      }
    });
    // Also trigger counters if in viewport
    const counter = document.querySelector('[data-count]');
    if (counter) {
      const rect = counter.getBoundingClientRect();
      if (rect.top < window.innerHeight) animateCounters();
    }
  }, 100);

  // Image preview
  window.previewImage = function(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(input.files[0]);
    }
  };

  // Confirm delete helper
  window.confirmDelete = function(msg) {
    return confirm(msg || 'Are you sure?');
  };

});
