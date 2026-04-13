/* ============================================================
   DeepMap — Application Logic
   ============================================================ */

const API_URL = 'http://localhost:8000';

// ---- State ----
let map, searchCircle, centerMarker;
let markersGroup = L.layerGroup();
let drawnItems = new L.FeatureGroup();
let drawControl;
let scoreChartInstance = null, typeChartInstance = null;
let radarChartInstance = null, priceChartInstance = null;
let currentBounds = null;
let currentListings = [];

// ---- DOM refs ----
const latInput = document.getElementById('latInput');
const lngInput = document.getElementById('lngInput');
const radiusInput = document.getElementById('radiusInput');
const searchBtn = document.getElementById('searchBtn');

// ---- Init Map ----
function initMap() {
    map = L.map('map', { zoomControl: false }).setView([10.855, 106.77], 13);
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OSM & CARTO',
        maxZoom: 19,
    }).addTo(map);

    markersGroup.addTo(map);
    drawnItems.addTo(map);

    // Drawing controls
    drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
            polygon: { allowIntersection: false, shapeOptions: { color: '#6c63ff', fillColor: '#6c63ff', fillOpacity: 0.08, weight: 2 } },
            rectangle: { shapeOptions: { color: '#6c63ff', fillColor: '#6c63ff', fillOpacity: 0.08, weight: 2 } },
            circle: false, circlemarker: false, marker: false, polyline: false,
        },
        edit: { featureGroup: drawnItems, remove: true },
    });
    map.addControl(drawControl);

    // Search circle for hot places
    searchCircle = L.circle([10.869638, 106.803820], {
        color: '#6c63ff', fillColor: '#6c63ff', fillOpacity: 0.06, weight: 1.5, dashArray: '6 4',
    });

    // Draw events
    map.on(L.Draw.Event.CREATED, function (e) {
        drawnItems.clearLayers();
        drawnItems.addLayer(e.layer);
        const bounds = e.layer.getBounds();
        currentBounds = {
            sw_lat: bounds.getSouthWest().lat,
            sw_lon: bounds.getSouthWest().lng,
            ne_lat: bounds.getNorthEast().lat,
            ne_lon: bounds.getNorthEast().lng,
        };
        fetchRealEstateRecommendations();
    });

    map.on(L.Draw.Event.DELETED, function () {
        currentBounds = null;
        markersGroup.clearLayers();
        document.getElementById('listingsContainer').innerHTML = '<p class="empty-state">Vẽ vùng chọn trên bản đồ để bắt đầu...</p>';
        document.getElementById('analyticsPanel').classList.add('hidden');
    });
}

// ---- Tabs ----
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('content' + capitalize(btn.dataset.tab)).classList.add('active');

        // Toggle draw controls vs circle
        if (btn.dataset.tab === 'hotplaces') {
            map.removeControl(drawControl);
            searchCircle.addTo(map);
        } else {
            map.addControl(drawControl);
            searchCircle.remove();
        }
        markersGroup.clearLayers();
        drawnItems.clearLayers();
        document.getElementById('analyticsPanel').classList.add('hidden');
    });
});
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ---- Real Estate: Fetch Recommendations ----
async function fetchRealEstateRecommendations() {
    if (!currentBounds) return;
    const statusEl = document.getElementById('reStatusMsg');
    statusEl.className = 'status-msg loading';
    statusEl.innerHTML = '<span class="spinner"></span> Đang phân tích khu vực...';

    const payload = {
        ...currentBounds,
        type: document.getElementById('filterType').value || null,
        max_price: parseFloat(document.getElementById('filterMaxPrice').value) || null,
        min_price: parseFloat(document.getElementById('filterMinPrice').value) || null,
        sort_by: document.getElementById('filterSort').value,
    };

    try {
        const res = await fetch(`${API_URL}/api/area-recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('API error');
        const data = await res.json();
        currentListings = data.listings || [];

        statusEl.className = 'status-msg success';
        statusEl.textContent = `Tìm thấy ${data.total} BĐS phù hợp.`;

        // Update stats
        document.getElementById('reTotalListings').textContent = data.total;
        if (data.area_analysis) {
            document.getElementById('reAreaScore').textContent = data.area_analysis.area_score;
            document.getElementById('reTotalPOIs').textContent = data.area_analysis.total_pois;
        }
        if (currentListings.length > 0) {
            const avg = currentListings.reduce((s, l) => s + l.price, 0) / currentListings.length;
            document.getElementById('reAvgPrice').textContent = avg.toFixed(1) + 'tr';
        }

        renderListings(currentListings);
        renderMapMarkers(currentListings, data.area_analysis);
        if (data.area_analysis) renderAnalytics(currentListings, data.area_analysis);
    } catch (err) {
        console.error(err);
        statusEl.className = 'status-msg error';
        statusEl.textContent = 'Lỗi kết nối Backend. Hãy chắc chắn server đang chạy.';
    }
}

// ---- Render Listing Cards ----
function renderListings(listings) {
    const container = document.getElementById('listingsContainer');
    if (listings.length === 0) {
        container.innerHTML = '<p class="empty-state">Không có BĐS nào trong khu vực này.</p>';
        return;
    }
    container.innerHTML = '';
    listings.forEach(l => {
        const scoreClass = l.overall_score >= 7 ? 'high' : l.overall_score >= 5 ? 'medium' : '';
        const card = document.createElement('div');
        card.className = 'listing-card';
        card.innerHTML = `
            <div class="listing-header">
                <div class="listing-title">${l.title}</div>
                <div class="listing-score ${scoreClass}">${l.overall_score}</div>
            </div>
            <div class="listing-meta">
                <span class="listing-badge badge-type">${l.type}</span>
                <span class="listing-badge badge-price">${l.price} tr/th</span>
                <span class="listing-badge badge-area">${l.area} m²</span>
                ${l.bedrooms ? `<span class="listing-badge" style="background:rgba(255,255,255,0.05);color:var(--text-secondary)">${l.bedrooms}PN</span>` : ''}
            </div>
            <div class="listing-address">${l.address}</div>
            <div class="listing-scores-bar">
                <div class="score-pill">Tiện ích<span>${l.amenity_score || '—'}</span></div>
                <div class="score-pill">Giá<span>${l.price_score || '—'}</span></div>
                <div class="score-pill">D.tích<span>${l.area_score || '—'}</span></div>
                <div class="score-pill">Đa dạng<span>${l.variety_score || '—'}</span></div>
            </div>
        `;
        card.addEventListener('click', () => {
            map.setView([l.lat, l.lon], 16);
            showDetailModal(l);
        });
        container.appendChild(card);
    });
}

// ---- Map Markers ----
function renderMapMarkers(listings, analysis) {
    markersGroup.clearLayers();

    // POI markers from area analysis
    if (analysis && analysis.top_pois) {
        analysis.top_pois.forEach(poi => {
            const icon = L.divIcon({
                html: `<div class="custom-marker" style="background:${getPoiColor(poi.type)};width:18px;height:18px;font-size:7px;">${poi.type.substring(0,2).toUpperCase()}</div>`,
                className: '', iconSize: [18, 18], iconAnchor: [9, 9],
            });
            L.marker([poi.lat, poi.lon], { icon }).addTo(markersGroup)
                .bindPopup(`<b>${poi.name}</b><br><span style="color:#8b8fa7">${poi.type} • ${poi.distance}m</span>`);
        });
    }

    // Listing markers
    listings.forEach(l => {
        const icon = L.divIcon({
            html: `<div class="house-marker">🏠</div>`,
            className: '', iconSize: [28, 28], iconAnchor: [14, 14],
        });
        L.marker([l.lat, l.lon], { icon }).addTo(markersGroup)
            .bindPopup(`<b style="font-size:13px">${l.title}</b><br><span style="color:var(--accent2)">${l.price} tr/th</span> • ${l.area}m²<br><span style="color:#8b8fa7">${l.address}</span><br><b style="color:#6c63ff">Score: ${l.overall_score}</b>`);
    });
}

function getPoiColor(type) {
    const colors = { hospital:'#ff4d6a', school:'#ffb347', marketplace:'#00d4aa', supermarket:'#00d4aa', bus_stop:'#64748b', restaurant:'#f59e0b', cafe:'#8b5cf6', attraction:'#ec4899', park:'#10b981' };
    return colors[type] || '#64748b';
}

// ---- Analytics Charts ----
function renderAnalytics(listings, analysis) {
    const panel = document.getElementById('analyticsPanel');
    panel.classList.remove('hidden');
    Chart.defaults.font.family = 'Inter';
    Chart.defaults.color = '#8b8fa7';

    // Radar chart
    if (analysis.category_scores) {
        if (radarChartInstance) radarChartInstance.destroy();
        const cats = analysis.category_scores;
        radarChartInstance = new Chart(document.getElementById('radarChart'), {
            type: 'radar',
            data: {
                labels: ['Y tế', 'Giáo dục', 'Mua sắm', 'Giao thông', 'Ăn uống', 'Giải trí'],
                datasets: [{
                    data: [cats.healthcare||0, cats.education||0, cats.shopping||0, cats.transport||0, cats.dining||0, cats.leisure||0],
                    backgroundColor: 'rgba(108,99,255,0.15)',
                    borderColor: '#6c63ff', borderWidth: 2,
                    pointBackgroundColor: '#6c63ff', pointRadius: 3,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { r: { max: 10, ticks: { display: false, stepSize: 2 }, grid: { color: 'rgba(255,255,255,0.05)' }, pointLabels: { font: { size: 9 }, color: '#8b8fa7' } } },
            },
        });
    }

    // Price chart
    if (listings.length > 0) {
        if (priceChartInstance) priceChartInstance.destroy();
        const sorted = [...listings].sort((a,b) => a.price - b.price);
        priceChartInstance = new Chart(document.getElementById('priceChart'), {
            type: 'bar',
            data: {
                labels: sorted.map(l => l.title.substring(0, 12) + '...'),
                datasets: [{
                    data: sorted.map(l => l.price),
                    backgroundColor: sorted.map(l => l.price > 10 ? '#ff4d6a' : l.price > 5 ? '#ffb347' : '#00d4aa'),
                    borderRadius: 4,
                }],
            },
            options: {
                indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { ticks: { font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.03)' } }, y: { ticks: { font: { size: 8 } }, grid: { display: false } } },
            },
        });
    }
}

// ---- Detail Modal ----
function showDetailModal(listing) {
    const modal = document.getElementById('detailModal');
    const content = document.getElementById('modalContent');
    content.innerHTML = `
        <button class="modal-close" onclick="document.getElementById('detailModal').classList.add('hidden')">&times;</button>
        <div class="detail-title">${listing.title}</div>
        <div class="detail-address">📍 ${listing.address}</div>
        <div class="detail-grid">
            <div class="detail-item"><div class="detail-item-label">Giá thuê</div><div class="detail-item-value" style="color:var(--accent2)">${listing.price} tr/th</div></div>
            <div class="detail-item"><div class="detail-item-label">Diện tích</div><div class="detail-item-value">${listing.area} m²</div></div>
            <div class="detail-item"><div class="detail-item-label">Phòng ngủ</div><div class="detail-item-value">${listing.bedrooms || '—'}</div></div>
            <div class="detail-item"><div class="detail-item-label">Phòng tắm</div><div class="detail-item-value">${listing.bathrooms || '—'}</div></div>
            <div class="detail-item"><div class="detail-item-label">Điểm tổng thể</div><div class="detail-item-value" style="color:var(--accent)">${listing.overall_score}</div></div>
            <div class="detail-item"><div class="detail-item-label">Điểm tiện ích</div><div class="detail-item-value">${listing.amenity_score || '—'}</div></div>
        </div>
        <div class="detail-amenities">${(listing.amenities || []).map(a => `<span class="detail-amenity">${a}</span>`).join('')}</div>
        <div class="detail-desc">${listing.description || ''}</div>
        ${listing.nearby_pois && listing.nearby_pois.length > 0 ? `
        <div class="detail-pois">
            <h4>Tiện ích gần đây</h4>
            <div class="detail-poi-list">${listing.nearby_pois.map(p => `<div class="detail-poi"><span>${p.name}</span><span style="color:var(--text-muted)">${p.distance}m</span></div>`).join('')}</div>
        </div>` : ''}
    `;
    modal.classList.remove('hidden');
}
document.getElementById('modalOverlay').addEventListener('click', () => {
    document.getElementById('detailModal').classList.add('hidden');
});

// ---- Close Analytics ----
document.getElementById('closeAnalytics').addEventListener('click', () => {
    document.getElementById('analyticsPanel').classList.add('hidden');
});

// ---- Filter changes trigger re-fetch ----
['filterType', 'filterMinPrice', 'filterMaxPrice', 'filterSort'].forEach(id => {
    document.getElementById(id).addEventListener('change', () => {
        if (currentBounds) fetchRealEstateRecommendations();
    });
});

// ---- Hot Places Logic (preserved) ----
radiusInput.addEventListener('input', (e) => {
    document.getElementById('radiusValue').textContent = `${e.target.value}m`;
    if (searchCircle._map) searchCircle.setRadius(parseFloat(e.target.value));
});

function getScoreStyle(score) {
    if (score >= 8) return { bg: '#ff4d6a', text: 'color:var(--danger)' };
    if (score >= 6) return { bg: '#ffb347', text: 'color:var(--warning)' };
    if (score >= 4) return { bg: '#6c63ff', text: 'color:var(--accent)' };
    return { bg: '#64748b', text: 'color:var(--text-muted)' };
}

searchBtn.addEventListener('click', async () => {
    const lat = parseFloat(latInput.value);
    const lon = parseFloat(lngInput.value);
    const radius = parseInt(radiusInput.value);

    searchCircle.setLatLng([lat, lon]);
    searchCircle.setRadius(radius);
    map.panTo([lat, lon]);

    searchBtn.innerHTML = '<span class="spinner"></span> Đang xử lý...';
    searchBtn.disabled = true;
    const statusMsg = document.getElementById('hpStatusMsg');
    statusMsg.className = 'status-msg loading';
    statusMsg.innerHTML = '<span class="spinner"></span> Đang kết nối Backend...';

    try {
        const response = await fetch(`${API_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat, lon, radius }),
        });
        if (!response.ok) throw new Error('API error');
        const pois = await response.json();
        if (pois.length === 0) throw new Error('Không tìm thấy địa điểm nào');

        updateHotPlacesDashboard(pois, lat, lon);
        statusMsg.className = 'status-msg success';
        statusMsg.textContent = `Tìm thấy ${pois.length} địa điểm.`;
    } catch (error) {
        statusMsg.className = 'status-msg error';
        statusMsg.textContent = `Lỗi: ${error.message}`;
    } finally {
        searchBtn.innerHTML = '🔍 Tìm kiếm địa điểm';
        searchBtn.disabled = false;
    }
});

function updateHotPlacesDashboard(pois, centerLat, centerLon) {
    const avgScore = pois.reduce((sum, p) => sum + p.hot_score, 0) / pois.length;
    const avgDist = pois.reduce((sum, p) => sum + p.distance, 0) / pois.length;
    const maxScore = Math.max(...pois.map(p => p.hot_score));

    document.getElementById('statTotal').textContent = pois.length;
    document.getElementById('statAvgScore').textContent = avgScore.toFixed(1);
    document.getElementById('statAvgDist').textContent = (avgDist / 1000).toFixed(2) + 'km';
    document.getElementById('statMaxScore').textContent = maxScore.toFixed(1);

    markersGroup.clearLayers();
    L.marker([centerLat, centerLon]).bindPopup('<b>Vị trí Trung tâm</b>').addTo(markersGroup);

    const listContainer = document.getElementById('poiList');
    listContainer.innerHTML = '';
    pois.sort((a, b) => b.hot_score - a.hot_score);

    pois.forEach(poi => {
        const style = getScoreStyle(poi.hot_score);
        const distKm = (poi.distance / 1000).toFixed(2);

        const icon = L.divIcon({
            html: `<div class="custom-marker" style="background-color:${style.bg};width:24px;height:24px;">${poi.hot_score.toFixed(1)}</div>`,
            className: '', iconSize: [24, 24], iconAnchor: [12, 12],
        });
        L.marker([poi.lat, poi.lon], { icon }).addTo(markersGroup)
            .bindPopup(`<b>${poi.name}</b><br><span style="color:#8b8fa7">${poi.type} • ${distKm}km</span>`);

        const item = document.createElement('div');
        item.className = 'poi-item';
        item.innerHTML = `
            <div><div class="poi-name">${poi.name}</div><div class="poi-meta">${poi.type} • ${distKm}km</div></div>
            <div class="poi-score" style="${style.text}">${poi.hot_score.toFixed(1)}</div>
        `;
        item.addEventListener('click', () => map.setView([poi.lat, poi.lon], 17));
        listContainer.appendChild(item);
    });

    map.fitBounds(searchCircle.getBounds(), { padding: [30, 30] });

    // Charts
    const panel = document.getElementById('analyticsPanel');
    panel.classList.remove('hidden');
    renderHotPlacesCharts(pois);
}

function renderHotPlacesCharts(pois) {
    Chart.defaults.font.family = 'Inter';
    Chart.defaults.color = '#8b8fa7';
    const top = pois.slice(0, 10);

    if (scoreChartInstance) scoreChartInstance.destroy();
    scoreChartInstance = new Chart(document.getElementById('scoreChart'), {
        type: 'bar',
        data: {
            labels: top.map(p => p.name.substring(0, 10) + '...'),
            datasets: [{ data: top.map(p => p.hot_score), backgroundColor: top.map(p => getScoreStyle(p.hot_score).bg), borderRadius: 4 }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { max: 10, ticks: { font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.03)' } } },
        },
    });

    const typeCounts = {};
    pois.forEach(p => typeCounts[p.type] = (typeCounts[p.type] || 0) + 1);
    if (typeChartInstance) typeChartInstance.destroy();
    typeChartInstance = new Chart(document.getElementById('typeChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(typeCounts),
            datasets: [{ data: Object.values(typeCounts), backgroundColor: ['#6c63ff','#ffb347','#00d4aa','#ec4899','#8b5cf6','#f59e0b'], borderWidth: 0 }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'right', labels: { boxWidth: 8, font: { size: 9 }, color: '#8b8fa7' } } },
            cutout: '70%',
        },
    });
}

// ---- Init ----
window.onload = initMap;
