// ═══════════════════════════════════════════════════════════════
//  CEIRS THEME ENGINE – Shared across all pages
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

    // ─── 1. ADVANCED PARTICLE SYSTEM ───
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let w, h, particles = [], mouse = { x: null, y: null };

        function resizeCanvas() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        document.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
        document.addEventListener('mouseleave', () => { mouse.x = null; mouse.y = null; });

        class Particle {
            constructor() { this.reset(); }
            reset() {
                this.x = Math.random() * w;
                this.y = Math.random() * h;
                this.size = Math.random() * 2.2 + 0.5;
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;
                this.opacity = Math.random() * 0.35 + 0.08;
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x < 0 || this.x > w || this.y < 0 || this.y > h) this.reset();
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(77, 143, 143, ${this.opacity})`;
                ctx.shadowColor = 'rgba(77, 143, 143, 0.1)';
                ctx.shadowBlur = 6;
                ctx.fill();
            }
        }

        function initParticles(count = 200) {
            particles = [];
            for (let i = 0; i < count; i++) particles.push(new Particle());
        }
        initParticles();

        function drawConnections() {
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        const alpha = (1 - dist / 120) * 0.15;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(77, 143, 143, ${alpha})`;
                        ctx.lineWidth = 0.6;
                        ctx.stroke();
                    }
                }
            }
            if (mouse.x !== null && mouse.y !== null) {
                for (const p of particles) {
                    const dx = p.x - mouse.x;
                    const dy = p.y - mouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 150) {
                        const alpha = (1 - dist / 150) * 0.2;
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(mouse.x, mouse.y);
                        ctx.strokeStyle = `rgba(201, 168, 94, ${alpha})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
        }

        function animateParticles() {
            ctx.clearRect(0, 0, w, h);
            particles.forEach(p => { p.update(); p.draw(); });
            drawConnections();
            requestAnimationFrame(animateParticles);
        }
        animateParticles();
    }

    // ─── 2. 3D BLOCKCHAIN VISUALIZATION ───
    const chainCanvas = document.getElementById('chainCanvas');
    if (chainCanvas) {
        const chainCtx = chainCanvas.getContext('2d');
        let chainW, chainH;

        function resizeChain() {
            const rect = chainCanvas.parentElement.getBoundingClientRect();
            chainCanvas.width = chainCanvas.clientWidth || rect.width - 40;
            chainCanvas.height = chainCanvas.clientHeight || 200;
            chainW = chainCanvas.width;
            chainH = chainCanvas.height;
        }
        window.addEventListener('resize', resizeChain);
        setTimeout(resizeChain, 100);

        const blocks = [];
        const NUM_BLOCKS = 18;
        for (let i = 0; i < NUM_BLOCKS; i++) {
            blocks.push({
                x: 0, y: 0, w: 36, h: 42,
                phase: Math.random() * Math.PI * 2,
                speed: 0.008 + Math.random() * 0.006,
                hue: 160 + Math.random() * 30,
                offsetY: (Math.random() - 0.5) * 12,
                hash: '0x' + Array.from({ length: 6 }, () => Math.floor(Math.random() * 16).toString(16)).join('')
            });
        }

        function drawChain() {
            if (!chainW || !chainH) return;
            chainCtx.clearRect(0, 0, chainW, chainH);

            const centerY = chainH / 2;
            const spacing = Math.min(48, (chainW - 40) / (NUM_BLOCKS + 1));
            const startX = 30;

            // connections
            for (let i = 0; i < blocks.length - 1; i++) {
                const b1 = blocks[i], b2 = blocks[i + 1];
                const x1 = startX + i * spacing + b1.w / 2;
                const y1 = centerY + Math.sin(Date.now() * b1.speed + b1.phase) * 14 + b1.offsetY;
                const x2 = startX + (i + 1) * spacing + b2.w / 2;
                const y2 = centerY + Math.sin(Date.now() * b2.speed + b2.phase) * 14 + b2.offsetY;

                const grad = chainCtx.createLinearGradient(x1, y1, x2, y2);
                grad.addColorStop(0, 'rgba(42, 107, 111, 0.2)');
                grad.addColorStop(0.5, 'rgba(201, 168, 94, 0.15)');
                grad.addColorStop(1, 'rgba(42, 107, 111, 0.2)');
                chainCtx.beginPath();
                chainCtx.moveTo(x1, y1);
                chainCtx.lineTo(x2, y2);
                chainCtx.strokeStyle = grad;
                chainCtx.lineWidth = 2;
                chainCtx.shadowColor = 'rgba(42, 107, 111, 0.05)';
                chainCtx.shadowBlur = 8;
                chainCtx.stroke();
                chainCtx.shadowBlur = 0;

                chainCtx.beginPath();
                chainCtx.arc((x1 + x2) / 2, (y1 + y2) / 2, 2, 0, Math.PI * 2);
                chainCtx.fillStyle = 'rgba(201, 168, 94, 0.15)';
                chainCtx.fill();
            }

            // blocks
            for (let i = 0; i < blocks.length; i++) {
                const b = blocks[i];
                const x = startX + i * spacing;
                const y = centerY + Math.sin(Date.now() * b.speed + b.phase) * 14 + b.offsetY - b.h / 2;
                const isSelected = i === Math.floor(Date.now() / 1200) % blocks.length;

                chainCtx.shadowColor = isSelected ? 'rgba(201, 168, 94, 0.15)' : 'rgba(42, 107, 111, 0.05)';
                chainCtx.shadowBlur = isSelected ? 25 : 8;

                const grad = chainCtx.createLinearGradient(x, y, x + b.w, y + b.h);
                const alpha = isSelected ? 0.9 : 0.5;
                grad.addColorStop(0, `rgba(42, 107, 111, ${alpha})`);
                grad.addColorStop(1, `rgba(30, 80, 80, ${alpha * 0.7})`);
                chainCtx.fillStyle = grad;
                chainCtx.shadowColor = isSelected ? 'rgba(201, 168, 94, 0.2)' : 'rgba(42, 107, 111, 0.05)';
                chainCtx.shadowBlur = isSelected ? 30 : 8;

                const r = 6;
                chainCtx.beginPath();
                chainCtx.moveTo(x + r, y);
                chainCtx.lineTo(x + b.w - r, y);
                chainCtx.quadraticCurveTo(x + b.w, y, x + b.w, y + r);
                chainCtx.lineTo(x + b.w, y + b.h - r);
                chainCtx.quadraticCurveTo(x + b.w, y + b.h, x + b.w - r, y + b.h);
                chainCtx.lineTo(x + r, y + b.h);
                chainCtx.quadraticCurveTo(x, y + b.h, x, y + b.h - r);
                chainCtx.lineTo(x, y + r);
                chainCtx.quadraticCurveTo(x, y, x + r, y);
                chainCtx.closePath();
                chainCtx.fill();
                chainCtx.shadowBlur = 0;

                chainCtx.strokeStyle = isSelected ? 'rgba(201, 168, 94, 0.5)' : 'rgba(42, 107, 111, 0.1)';
                chainCtx.lineWidth = isSelected ? 1.5 : 0.5;
                chainCtx.stroke();

                chainCtx.fillStyle = isSelected ? '#eef4fa' : 'rgba(160, 179, 192, 0.4)';
                chainCtx.font = isSelected ? 'bold 10px Inter, sans-serif' : '8px Inter, sans-serif';
                chainCtx.textAlign = 'center';
                chainCtx.textBaseline = 'middle';
                chainCtx.fillText(i + 1, x + b.w / 2, y + b.h / 2 - 2);

                if (isSelected) {
                    chainCtx.fillStyle = 'rgba(160, 179, 192, 0.3)';
                    chainCtx.font = '5px monospace';
                    chainCtx.fillText(b.hash.slice(0, 6), x + b.w / 2, y + b.h / 2 + 12);
                }
            }
            requestAnimationFrame(drawChain);
        }
        setTimeout(() => { resizeChain(); drawChain(); }, 150);
    }

    // ─── 3. SECURITY GAUGE ───
    const gaugeCanvas = document.getElementById('gaugeCanvas');
    if (gaugeCanvas) {
        const gaugeCtx = gaugeCanvas.getContext('2d');
        const gaugeValue = document.getElementById('gaugeValue');
        let currentPercent = 92;

        function drawGauge(percent) {
            const cx = 100, cy = 100, radius = 82;
            gaugeCtx.clearRect(0, 0, 200, 200);

            gaugeCtx.beginPath();
            gaugeCtx.arc(cx, cy, radius, 0.75 * Math.PI, 2.25 * Math.PI);
            gaugeCtx.strokeStyle = 'rgba(42, 107, 111, 0.08)';
            gaugeCtx.lineWidth = 10;
            gaugeCtx.lineCap = 'round';
            gaugeCtx.stroke();

            const start = 0.75 * Math.PI;
            const end = 0.75 * Math.PI + 1.5 * Math.PI * (percent / 100);
            const grad = gaugeCtx.createLinearGradient(0, 0, 200, 200);
            grad.addColorStop(0, '#2a6b6f');
            grad.addColorStop(0.6, '#4d8f8f');
            grad.addColorStop(1, '#c9a85e');
            gaugeCtx.beginPath();
            gaugeCtx.arc(cx, cy, radius, start, end);
            gaugeCtx.strokeStyle = grad;
            gaugeCtx.lineWidth = 10;
            gaugeCtx.lineCap = 'round';
            gaugeCtx.shadowColor = 'rgba(42, 107, 111, 0.2)';
            gaugeCtx.shadowBlur = 20;
            gaugeCtx.stroke();
            gaugeCtx.shadowBlur = 0;

            gaugeCtx.beginPath();
            gaugeCtx.arc(cx, cy, 6, 0, Math.PI * 2);
            gaugeCtx.fillStyle = 'rgba(42, 107, 111, 0.15)';
            gaugeCtx.fill();

            gaugeCtx.fillStyle = 'var(--text-primary)';
            gaugeCtx.font = 'bold 22px Inter, sans-serif';
            gaugeCtx.textAlign = 'center';
            gaugeCtx.textBaseline = 'middle';
            gaugeCtx.fillText(Math.round(percent) + '%', cx, cy - 6);

            gaugeCtx.fillStyle = 'var(--text-muted)';
            gaugeCtx.font = '9px Inter, sans-serif';
            gaugeCtx.fillText('SECURE', cx, cy + 22);

            if (gaugeValue) gaugeValue.textContent = Math.round(percent) + '%';
        }

        let targetPercent = 92;
        function animateGauge() {
            targetPercent = 92 + Math.random() * 7;
            const step = () => {
                const diff = targetPercent - currentPercent;
                if (Math.abs(diff) > 0.1) {
                    currentPercent += diff * 0.04;
                    drawGauge(currentPercent);
                    requestAnimationFrame(step);
                } else {
                    currentPercent = targetPercent;
                    drawGauge(currentPercent);
                }
            };
            step();
            setTimeout(animateGauge, 8000);
        }
        setTimeout(() => { currentPercent = 92; drawGauge(92); }, 200);
        setTimeout(animateGauge, 3000);
    }

    // ─── 4. COUNT-UP ANIMATION ───
    const countEls = document.querySelectorAll('.stat-number[data-count]');
    const obs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseFloat(el.getAttribute('data-count'));
                if (isNaN(target)) { el.textContent = el.getAttribute('data-count'); return; }
                let current = 0;
                const duration = 1200;
                const startTime = performance.now();

                function update(time) {
                    const progress = Math.min(1, (time - startTime) / duration);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const val = eased * target;
                    if (target % 1 === 0) el.textContent = Math.floor(val);
                    else el.textContent = val.toFixed(1);
                    if (progress < 1) requestAnimationFrame(update);
                    else el.textContent = target % 1 === 0 ? target : target.toFixed(1);
                }
                requestAnimationFrame(update);
                obs.unobserve(el);
            }
        });
    }, { threshold: 0.3 });
    countEls.forEach(el => obs.observe(el));

    // ─── 5. 3D TILT ON FEATURE CARDS ───
    document.querySelectorAll('.feature-card[data-tilt]').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const r = this.getBoundingClientRect();
            const x = e.clientX - r.left, y = e.clientY - r.top;
            const rx = ((y - r.height / 2) / r.height) * -6;
            const ry = ((x - r.width / 2) / r.width) * 6;
            this.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-8px) scale(1.01)`;
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = `perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0px) scale(1)`;
        });
    });

    // ─── 6. THEME TOGGLE ───
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    if (themeToggle) {
        let dark = true;
        themeToggle.addEventListener('click', () => {
            dark = !dark;
            document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
            themeIcon.className = dark ? 'fas fa-moon' : 'fas fa-sun';
        });
    }

    // ─── 7. LIVE BLOCK COUNTER & HASH ───
    let blockCount = 400013;
    setInterval(() => {
        blockCount += 1;
        const counter = document.getElementById('blockCounter');
        if (counter) counter.textContent = blockCount;
        const hashEl = document.getElementById('latestHash');
        if (hashEl) {
            const chars = '0123456789abcdef';
            let hash = '0x';
            for (let i = 0; i < 8; i++) hash += chars[Math.floor(Math.random() * 16)];
            hash += '…';
            for (let i = 0; i < 4; i++) hash += chars[Math.floor(Math.random() * 16)];
            hashEl.textContent = hash;
        }
    }, 3200);

    // ─── 8. SEARCH INTERACTION ───
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('focus', function() { this.parentElement.style.boxShadow = '0 0 40px rgba(42,107,111,0.06)'; });
        searchInput.addEventListener('blur', function() { this.parentElement.style.boxShadow = 'none'; });
    }

    console.log('🚀 CEIRS theme engine initialized.');
});