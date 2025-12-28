<template>
  <div class="about-container">
    <!-- Hero Section with Video Background -->
    <section class="hero-section">
      <div class="hero-overlay">
        <video autoplay loop muted playsinline class="hero-video">
          <source src="/film.mp4" type="video/mp4">
        </video>
        <div class="hero-content">
          <h1 class="hero-title">
            We Distribute<br>
            <span class="dynamic-text" ref="dynamicTextRef"></span>
          </h1>
        </div>
      </div>
    </section>

    <!-- Info Sections: white background, layered panels with left-right split -->
    <section class="mission-section panel-white">
      <div class="container">
        <div class="panel-row">
          <div class="panel-text">
            <h2 class="section-title">About Us</h2>
            <p class="panel-paragraph">
                Welcome to The Film Hub, your ultimate destination for all things cinema! At The Film Hub, we are passionate about film and dedicated to sharing that passion with our community of movie lovers.
            </p>
          </div>
          <div class="panel-image">
            <img src="/hollywood.jpeg" alt="About visual" />
          </div>
        </div>
      </div>
    </section>

    <section class="features-section panel-white">
      <div class="container">
        <div class="panel-row">
          <div class="panel-image">
            <img src="/discussion.png" alt="Community" />
          </div>
          <div class="panel-text">
            <h2 class="section-title">What We Offer</h2>
            <p class="panel-paragraph">Discover hidden gems and popular favorites tailored to your preferences, explore in-depth reviews analyzing storytelling and cinematography, and join our community of film enthusiasts for lively discussions and connections.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="gallery-section panel-white">
      <div class="container">
        <div class="panel-row">
          <div class="panel-text">
            <h3 class="section-title">Why Choose Us</h3>
            <p class="panel-paragraph">At The Film Hub, we celebrate each film as a unique journey. Our passionate team creates sincere, insightful content that explores cinema's power to inspire, touch hearts, and spread joy. Join us for an immersive cinematic adventure!</p>
          </div>
          <div class="panel-image">
            <img src="/film-shooting.jpg" alt="Feature image" />
          </div>
        </div>
      </div>
    </section>
    
    <!-- Full-width bottom photo -->
    <section class="bottom-photo">
      <img src="/shooting-film.jpg" alt="Shooting Film" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Dynamic text for hero section
const words = ['Passion of Life', 'Beauty Of Film', 'Stories of People']
const wordIndex = ref(0)
const dynamicTextRef = ref(null)

const updateWord = () => {
  if (dynamicTextRef.value) {
    dynamicTextRef.value.textContent = words[wordIndex.value]
    wordIndex.value = (wordIndex.value + 1) % words.length
  }
}

onMounted(() => {
  // Initialize dynamic text
  updateWord()
  setInterval(updateWord, 5000)
})
</script>

<style scoped>
.about-container {
  background-color: #000000;
  color: #ffffff;
}

/* Hero Section */
.hero-section {
  position: relative;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.7) 100%);
}

.hero-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.6);
}

.hero-content {
  position: absolute;
  bottom: 20%;
  left: 10%;
  z-index: 2;
  text-align: left;
  max-width: 1000px;
}

.hero-title {
  font-size: clamp(2.5rem, 8vw, 6rem);
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8);
  letter-spacing: -0.02em;
  line-height: 1.05;
  word-break: break-word;
}

.dynamic-text {
  color: #ffffff;
  display: block;
  animation: fadeIn 0.5s ease-in-out;
  min-height: 1.2em;
}

/* Mission Section */
.mission-section {
  padding: 6rem 0;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

.mission-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 4rem;
  align-items: center;
}

.mission-text h2 {
  font-size: 3rem;
  font-weight: 700;
  color: #f5c518;
  margin-bottom: 2rem;
}

.mission-description {
  font-size: 1.25rem;
  line-height: 1.7;
  color: #cccccc;
  margin-bottom: 2rem;
}

.mission-visual {
  display: flex;
  justify-content: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.stat-item {
  text-align: center;
  padding: 2rem;
  background: rgba(245, 197, 24, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(245, 197, 24, 0.2);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #f5c518;
  display: block;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  color: #cccccc;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Features Section */

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-size: 3rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 1rem;
}

.section-subtitle {
  font-size: 1.25rem;
  color: #cccccc;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* White panel styles for sections */
.panel-white {
  background: #ffffff;
  color: #000000;
  padding: 4rem 0;
}

.panel-row {
  display: flex;
  gap: 2rem;
  align-items: center;
  justify-content: center;
}

.panel-text {
  flex: 0 0 520px;
  max-width: 520px;
  padding: 1rem 2rem;
  font-size: 18px;
  font-weight: bold;
}

.panel-image {
  flex: 0 0 520px;
  max-width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 2rem;
}

.panel-image img {
  width: 100%;
  max-width: 520px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.panel-layer {
  background: transparent;
  padding: 0;
  border-radius: 0;
  margin-bottom: 1rem;
  border: none;
  box-shadow: none;
}

.panel-paragraph {
  color: #000000;
  line-height: 1.7;
  margin-bottom: 1rem;
}

.gallery-small img {
  width: 48%;
  margin-right: 4%;
  border-radius: 8px;
}

/* Bottom photo full-width */
.bottom-photo img {
  width: 100%;
  display: block;
  object-fit: cover;
}

/* Make section titles/text black inside white panels */
.panel-white .section-title {
  color: #000000 !important;
}
.panel-white .panel-text,
.panel-white .panel-text p {
  color: #000000 !important;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .mission-content {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .gallery-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(3, 250px);
  }

  .gallery-item.large {
    grid-row: span 1;
  }
}

/* Panels responsive adjustments */
@media (max-width: 1200px) {
  .panel-text,
  .panel-image {
    flex: 0 0 48%;
    max-width: 48%;
  }
  .panel-row {
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .panel-row {
    flex-direction: column;
    gap: 1rem;
  }
  .panel-text,
  .panel-image {
    flex: 1 1 100%;
    max-width: none;
  }
  .panel-text {
    padding: 0.75rem 1rem;
    font-size: 16px;
    font-weight: 400;
  }
  .panel-image {
    padding: 0.5rem 0.75rem;
  }
  .hero-title {
    font-size: clamp(2rem, 8vw, 3.5rem);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 4rem;
  }

  .section-title {
    font-size: 2.5rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .mission-section,
  .features-section,
  .gallery-section,
  .cta-section {
    padding: 4rem 0;
  }

  .cta-title {
    font-size: 2rem;
  }

  .stat-item {
    padding: 1.5rem;
  }

  .stat-number {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 3rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .cta-title {
    font-size: 1.8rem;
  }

  .feature-card {
    padding: 2rem 1.5rem;
  }
}
</style>