CREATE TABLE IF NOT EXISTS medications (
            med_id TEXT PRIMARY KEY,
            generic_name TEXT NOT NULL,
            therapeutic_class TEXT,
            form TEXT,
            strength TEXT,
            category TEXT,
            base_demand INTEGER,
            stocking_level INTEGER,
            is_cold_chain INTEGER,
            nrn TEXT
        );

CREATE TABLE IF NOT EXISTS companies (
            company_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT,
            city TEXT,
            is_manufacturer INTEGER,
            is_importer INTEGER,
            is_distributor INTEGER
        );

CREATE TABLE IF NOT EXISTS facilities(
            facility_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            facility_type TEXT,
            city TEXT,
            state TEXT,
            tier TEXT,
            has_cold_storage INTEGER,
            latitude REAL,
            longitude REAL
        );

CREATE TABLE IF NOT EXISTS brands(
            brand_id TEXT PRIMARY KEY,
            brand_name TEXT NOT NULL,
            med_id TEXT,
            manufacturer_id TEXT,
            unit_price INTEGER,
            is_innovator TEXT,
            counterfeit_risk TEXT,

            FOREIGN KEY (med_id) REFERENCES medications (med_id),
            FOREIGN KEY (manufacturer_id) REFERENCES companies(company_id)
        );

CREATE TABLE IF NOT EXISTS batches (
            batch_id TEXT PRIMARY KEY,
            brand_id TEXT NOT NULL,
            importer_id TEXT,
            batch_number TEXT,
            manufacturing_date TEXT,
            expiry_date TEXT,
            initial_quantity INTEGER,
            is_verified INTEGER,
            is_flagged INTEGER,

           FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
           FOREIGN KEY (importer_id) REFERENCES companies(company_id)
        );

CREATE TABLE IF NOT EXISTS inventory (
            inventory_id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL,
            batch_id TEXT NOT NULL,
            quantity INTEGER,
            reorder_point INTEGER,
            unit_price INTEGER,

            FOREIGN KEY (facility_id) REFERENCES facilities(facility_id),
            FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
           
        );

CREATE TABLE IF NOT EXISTS movements (
            movement_id TEXT PRIMARY KEY,
            facility_id TEXT,
            batch_id TEXT,
            inventory_id TEXT,
            movement_type TEXT,
            quantity_before INTEGER,
            quantity_change INTEGER,
            quantity_after INTEGER,
            timestamp TEXT,
            reference_id TEXT,
            source TEXT,
            reason TEXT,

            FOREIGN KEY (facility_id) REFERENCES facilities(facility_id)
        );

CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT,
            severity TEXT,
            facility_id TEXT,
            batch_id TEXT,
            timestamp TEXT,
            detected_at TEXT,
            details TEXT,
            data TEXT,  
            source TEXT,
            is_active INTEGER
        );

CREATE TABLE IF NOT EXISTS anomalies (
            anomaly_id TEXT PRIMARY KEY,
            anomaly_type TEXT,
            severity TEXT,
            facility_id TEXT,
            batch_id TEXT,
            timestamp TEXT,
            details TEXT,
            evidence TEXT,  
            source TEXT,
            is_active INTEGER
        );

CREATE TABLE agent_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    cycle_time TEXT,
    low_stock_count INTEGER,
    stockout_count INTEGER,
    active_anomaly_count INTEGER,
    critical_anomaly_count INTEGER,
    critical_anomaly_ids TEXT,  -- JSON: ["ANOM_001", "ANOM_002"]
    new_anomaly_ids TEXT,       -- Detected this cycle
    resolved_anomaly_ids TEXT,  -- Resolved this cycle
    actions_taken TEXT,         -- JSON: what agent did
    reasoning_summary TEXT      -- Brief explanation
);

CREATE INDEX IF NOT EXISTS idx_brands_med ON brands(med_id);
CREATE INDEX IF NOT EXISTS idx_batches_brand ON batches(brand_id);
CREATE INDEX IF NOT EXISTS idx_inventory_facility ON inventory(facility_id);
CREATE INDEX IF NOT EXISTS idx_inventory_batch ON inventory(batch_id);
CREATE INDEX IF NOT EXISTS idx_movements_facility ON movements(facility_id);
CREATE INDEX IF NOT EXISTS idx_movements_batch ON movements(batch_id);
CREATE INDEX IF NOT EXISTS idx_movements_timestamp ON movements(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);