// PetCheck — Enhanced main.js with modern animations

document.addEventListener('DOMContentLoaded', () => {
  
  // Animate confidence bars on results page
  const confFill = document.querySelector('.conf-fill');
  if (confFill) {
    const width = confFill.style.width;
    confFill.style.width = '0%';
    setTimeout(() => { 
      confFill.style.width = width; 
    }, 200);
  }

  // Animate prediction bars
  document.querySelectorAll('.pred-bar-fill').forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => { 
      bar.style.width = width; 
    }, 300);
  });

  // Highlight active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href === path || (path !== '/' && href !== '/' && path.startsWith(href)))) {
      link.style.color = 'var(--primary)';
      if (link.classList.contains('btn-nav')) {
        link.style.background = 'var(--primary)';
        link.style.color = 'white';
      }
    }
  });

  // Add scroll reveal animation for cards
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  // Apply fade-up animation to cards
  document.querySelectorAll('.feature-card, .step, .vet-card-modern, .article-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Add hover effect for buttons
  document.querySelectorAll('.btn-primary, .btn-ghost, .vet-btn-call, .vet-btn-email').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
    });
    btn.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });

  // Loading animation for upload page
  const analyzeBtn = document.getElementById('analyzeBtn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', function() {
      this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
      this.disabled = true;
    });
  }

  // Add tooltip functionality for vet cards
  document.querySelectorAll('.vet-card-modern').forEach(card => {
    card.addEventListener('click', (e) => {
      if (e.target.tagName !== 'A' && !e.target.closest('a')) {
        const phone = card.querySelector('.vet-btn-call')?.getAttribute('href');
        if (phone) {
          window.location.href = phone;
        }
      }
    });
  });

  // Dynamic year in footer
  const footerYear = document.querySelector('.footer-copy');
  if (footerYear) {
    footerYear.innerHTML = footerYear.innerHTML.replace('2024', new Date().getFullYear());
  }
});

// Add floating animation to hero elements
function addFloatingAnimation() {
  const floatingElements = document.querySelectorAll('.phone-mockup, .hero-visual');
  floatingElements.forEach(el => {
    if (!el.style.animation) {
      el.style.animation = 'float 4s ease-in-out infinite';
    }
  });
}

// Call after load
window.addEventListener('load', addFloatingAnimation);

// Footer search functionality
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.footer-search input');
  const searchBtn = document.querySelector('.footer-search button');
  
  function performSearch() {
    const query = searchInput.value.trim();
    if (query) {
      window.location.href = '/articles?search=' + encodeURIComponent(query);
    }
  }
  
  if (searchBtn) {
    searchBtn.addEventListener('click', performSearch);
  }
  
  if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        performSearch();
      }
    });
  }
});