# 🛰️ Space Weather Impact Modeling System

A real-time 3D visualization and predictive modeling system that quantifies operational impacts of space weather on individual satellites. Built with React, Three.js, and advanced physics models.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### Core Functionality
- **Real-time 3D Visualization** - Interactive Earth, satellites, and magnetosphere
- **Physics-Based Impact Models** - Atmospheric drag, radiation dose, signal degradation
- **Risk Assessment** - Per-satellite analysis with actionable recommendations
- **Space Weather Integration** - Live data from NOAA and NASA APIs
- **Historical Replay** - Analyze past geomagnetic storms

### Impact Calculations
1. **Atmospheric Drag** (NRLMSISE-00 model)
   - Orbit decay prediction
   - Reboost scheduling
   
2. **Radiation Effects** (AP-8/AE-8 models)
   - Cumulative dose tracking
   - SEU probability estimation
   
3. **Communication Degradation**
   - Signal quality assessment
   - GPS error prediction
   - Blackout duration forecasting

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Earth.jsx                    # 3D Earth model
│   │   ├── Satellite.jsx                # Satellite sprites
│   │   ├── Magnetosphere.jsx            # Van Allen belts
│   │   ├── SpaceWeatherParticles.jsx    # Solar wind visualization
│   │   ├── ImpactDashboard.jsx          # Impact analysis panel
│   │   └── SpaceWeatherControls.jsx     # Control panel
│   ├── api/
│   │   ├── tle.js                       # TLE data fetching
│   │   └── spaceWeather.js              # Space weather APIs
│   ├── utils/
│   │   ├── orbit.js                     # Orbital mechanics
│   │   └── impactModels.js              # Physics calculations
│   ├── App.jsx                          # Main application
│   ├── App.css                          # Main styles
│   └── main.jsx                         # Entry point
├── public/
│   └── assets/
│       └── satellite.png                # Satellite icon
└── package.json
```

## 🚀 Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd space-weather-impact-system
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Add Satellite Icon
Create `public/assets/satellite.png` or use a placeholder image:
```bash
mkdir -p public/assets
# Add your satellite icon here (any small PNG will work for testing)
```

### Step 4: Run Development Server
```bash
npm run dev
```

Open http://localhost:5173 in your browser!

## 🎮 Usage

### Basic Controls
- **Mouse Drag** - Rotate view
- **Mouse Wheel** - Zoom in/out
- **Right Click Drag** - Pan camera

### Space Weather Controls
1. **Kp Index** (0-9) - Geomagnetic activity level
2. **F10.7 Solar Flux** (70-250) - Solar radiation intensity
3. **Solar Wind Speed** (300-900 km/s) - Particle velocity
4. **Proton Flux** (1-10,000 pfu) - Radiation storm intensity

### Quick Scenarios
- **Quiet Conditions** - Normal space weather
- **Moderate Storm** - G2 geomagnetic storm
- **Severe Storm** - G4 extreme event

### Satellite Selection
Click on any satellite or select from the list to view detailed impact analysis.

## 📊 Impact Metrics Explained

### Orbit Decay Rate
- **Normal**: < 10 m/day
- **Elevated**: 10-50 m/day
- **High**: 50-100 m/day
- **Critical**: > 100 m/day

### SEU Probability
- **Low**: < 5%
- **Moderate**: 5-20%
- **High**: 20-50%
- **Critical**: > 50%

### Signal Quality
- **Good**: < 10 dB loss
- **Degraded**: 10-30 dB loss
- **Severe**: > 30 dB loss

## 🔬 Technical Details

### Physics Models

#### 1. Atmospheric Drag
```javascript
F_drag = 0.5 × ρ × v² × Cd × A
Δh = (F_drag / m) × Δt
```
Where:
- ρ = atmospheric density (varies with Kp, F10.7)
- v = orbital velocity
- Cd = drag coefficient
- A = cross-sectional area
- m = satellite mass

#### 2. Radiation Dose
Based on AP-8 (protons) and AE-8 (electrons) models:
- Van Allen belt intensity mapping
- Storm-time enhancement factors
- Cumulative dose tracking

#### 3. Signal Degradation
Ionospheric scintillation model:
- TEC (Total Electron Content) variations
- Latitude-dependent effects
- Frequency-dependent fading

### Data Sources
- **NOAA SWPC** - Real-time space weather data
- **CelesTrak** - Satellite TLE data
- **NASA DONKI** - CME and solar flare events

## 🎓 For Dissertation Use

### Validation Methodology
1. **Historical Event Testing**
   - Halloween Storm (2003)
   - St. Patrick's Day Storm (2015)
   - Starlink Loss Event (2022)

2. **Accuracy Metrics**
   - Compare predictions vs. actual anomalies
   - Calculate precision, recall, F1-score
   - Statistical validation

### Documentation Requirements
- Methodology chapter: Explain physics models
- Results chapter: Present case studies
- Code documentation: Inline comments
- User manual: System usage guide

## 🛠️ Customization

### Adding New Satellites
```javascript
// In App.jsx, modify satellite loading
const data = parseTLE(text)
setSatellites(data.slice(0, 20)) // Increase from 10 to 20
```

### Adjusting Physics Models
Edit `src/utils/impactModels.js`:
```javascript
// Customize drag coefficient per satellite type
const dragCoeff = satelliteType === 'ISS' ? 2.2 : 1.8
```

### Adding New Impact Types
1. Create calculation function in `impactModels.js`
2. Add visualization in `ImpactDashboard.jsx`
3. Update recommendations generator

## 📝 Development Roadmap

### Phase 1 (Current)
- ✅ 3D visualization
- ✅ Basic impact models
- ✅ Real-time space weather
- ✅ Risk assessment

### Phase 2 (Future)
- [ ] Machine learning predictions
- [ ] Historical event database
- [ ] Multi-satellite comparison
- [ ] PDF report generation

### Phase 3 (Advanced)
- [ ] Backend API (Python Flask)
- [ ] Database integration
- [ ] User authentication
- [ ] Mission planning tools

## 🐛 Troubleshooting

### Common Issues

**Satellites not loading:**
```javascript
// Check TLE API in console
// Fallback: Use local TLE file
import localTLE from './data/satellites.txt'
```

**Space weather data fails:**
- Using default values as fallback
- Check NOAA API status
- Verify CORS is enabled

**Performance issues:**
- Reduce satellite count (line 27 in App.jsx)
- Disable particles (uncheck in controls)
- Lower graphics quality

## 📄 License

MIT License - Free for academic and commercial use

## 👨‍💻 Author

Your Name - Dissertation Project 2024/2025

## 🙏 Acknowledgments

- NOAA Space Weather Prediction Center
- NASA DONKI API
- CelesTrak satellite database
- Three.js & React-Three-Fiber communities

## 📚 References

1. NRLMSISE-00 Atmospheric Model
2. AP-8/AE-8 Radiation Belt Models
3. Space Weather Impact on Satellites (2023)
4. Geomagnetic Storm Effects (NOAA)

---

**For questions or issues, please contact: your.email@university.edu**

Last Updated: January 2026