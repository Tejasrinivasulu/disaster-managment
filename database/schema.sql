-- Disaster Response System schema (PostgreSQL-compatible)
-- SQLite is used for local development when DATABASE_URL points to sqlite.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS disasters (
    id SERIAL PRIMARY KEY,
    disaster_type VARCHAR(100) NOT NULL,
    subtype VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date TIMESTAMPTZ,
    location_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    severity VARCHAR(50),
    status VARCHAR(50),
    affected_population INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS disaster_zones (
    id SERIAL PRIMARY KEY,
    disaster_id INTEGER REFERENCES disasters(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    population INTEGER DEFAULT 0,
    population_density DOUBLE PRECISION DEFAULT 0,
    vulnerability_score DOUBLE PRECISION DEFAULT 0.5,
    accessibility_score DOUBLE PRECISION DEFAULT 0.7,
    building_damage_pct DOUBLE PRECISION DEFAULT 0,
    road_damage_pct DOUBLE PRECISION DEFAULT 0,
    rainfall DOUBLE PRECISION DEFAULT 0,
    humidity DOUBLE PRECISION DEFAULT 50,
    severity VARCHAR(50),
    priority VARCHAR(50),
    priority_override BOOLEAN DEFAULT FALSE,
    food_demand DOUBLE PRECISION DEFAULT 0,
    water_demand_litres DOUBLE PRECISION DEFAULT 0,
    medical_kit_demand DOUBLE PRECISION DEFAULT 0,
    shelter_demand DOUBLE PRECISION DEFAULT 0
);

CREATE TABLE IF NOT EXISTS resource_depots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    capacity INTEGER DEFAULT 10000,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    depot_id INTEGER REFERENCES resource_depots(id) ON DELETE CASCADE,
    resource_type VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity_available DOUBLE PRECISION DEFAULT 0,
    quantity_reserved DOUBLE PRECISION DEFAULT 0,
    quantity_deployed DOUBLE PRECISION DEFAULT 0,
    unit VARCHAR(50) DEFAULT 'units',
    status VARCHAR(50),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resource_allocations (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES disaster_zones(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    resource_type VARCHAR(100) NOT NULL,
    requested_quantity DOUBLE PRECISION DEFAULT 0,
    allocated_quantity DOUBLE PRECISION DEFAULT 0,
    shortage DOUBLE PRECISION DEFAULT 0,
    coverage_pct DOUBLE PRECISION DEFAULT 0,
    priority VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS field_teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    leader_name VARCHAR(255) NOT NULL,
    members_count INTEGER DEFAULT 5,
    skills TEXT,
    latitude DOUBLE PRECISION DEFAULT 0,
    longitude DOUBLE PRECISION DEFAULT 0,
    status VARCHAR(50),
    assigned_disaster_id INTEGER REFERENCES disasters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS missions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    disaster_id INTEGER REFERENCES disasters(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES disaster_zones(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES field_teams(id) ON DELETE CASCADE,
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resources_json JSONB,
    priority VARCHAR(50),
    status VARCHAR(50),
    deadline TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS demand_predictions (
    id SERIAL PRIMARY KEY,
    disaster_id INTEGER REFERENCES disasters(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES disaster_zones(id) ON DELETE CASCADE,
    food_demand DOUBLE PRECISION DEFAULT 0,
    water_demand_litres DOUBLE PRECISION DEFAULT 0,
    medical_kit_demand DOUBLE PRECISION DEFAULT 0,
    shelter_demand DOUBLE PRECISION DEFAULT 0,
    base_food DOUBLE PRECISION DEFAULT 0,
    base_water DOUBLE PRECISION DEFAULT 0,
    base_medical DOUBLE PRECISION DEFAULT 0,
    base_shelter DOUBLE PRECISION DEFAULT 0,
    vulnerability_adjustment DOUBLE PRECISION DEFAULT 0,
    confidence JSONB,
    model_used JSONB,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS field_reports (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES disaster_zones(id) ON DELETE CASCADE,
    reporter_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    population_affected INTEGER,
    building_damage_pct DOUBLE PRECISION,
    road_damage_pct DOUBLE PRECISION,
    severity VARCHAR(50),
    accessibility_score DOUBLE PRECISION,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS priority_overrides (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES disaster_zones(id) ON DELETE CASCADE,
    previous_priority VARCHAR(50) NOT NULL,
    new_priority VARCHAR(50) NOT NULL,
    reason TEXT NOT NULL,
    changed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scenarios (
    id SERIAL PRIMARY KEY,
    disaster_id INTEGER REFERENCES disasters(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    response_speed VARCHAR(50) DEFAULT 'normal',
    available_food DOUBLE PRECISION DEFAULT 0,
    available_water DOUBLE PRECISION DEFAULT 0,
    available_medical DOUBLE PRECISION DEFAULT 0,
    available_shelter DOUBLE PRECISION DEFAULT 0,
    transport_capacity DOUBLE PRECISION DEFAULT 0,
    results_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    depot_id INTEGER REFERENCES resource_depots(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES disaster_zones(id) ON DELETE CASCADE,
    distance_km DOUBLE PRECISION DEFAULT 0,
    estimated_time_hours DOUBLE PRECISION DEFAULT 0,
    vehicle_type VARCHAR(100) DEFAULT 'truck',
    resources_json JSONB,
    route_geometry JSONB,
    provider VARCHAR(50) DEFAULT 'local_haversine',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INTEGER,
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
