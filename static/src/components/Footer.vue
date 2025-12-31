<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="copyright">
        &copy; 2026 Film Hub. All rights reserved.
      </div>
      <div class="contact">
        <span>Contact: </span>
        <a href="mailto:glim137137@gmail.com" class="contact-link">
          glim137137@gmail.com
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Footer component for Film Hub
</script>

<style scoped>
.footer {
  background-color: #000000;
  border-top: 2px solid #333333;
  padding: 2rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.copyright {
  color: #cccccc;
  font-size: 0.9rem;
}

.contact {
  color: #cccccc;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.contact-link {
  color: #5799ef;
  text-decoration: none;
  transition: color 0.3s ease;
}

.contact-link:hover {
  color: #4682d6;
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .copyright,
  .contact {
    font-size: 0.8rem;
  }
}
</style>
