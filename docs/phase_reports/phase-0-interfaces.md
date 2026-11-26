# Phase 0 interface inventory

| Module | Existing callers | Contract |
| --- | --- | --- |
| features | verify_phase4, clustering tests | extract_wallet_features returns a wallet-address-keyed Polars frame with 24 finite numerical features. |
| anomaly | verify_phase4 | IsolationForestConfig and AnomalyModel.load expose model, dataset_size, trained_at and config.n_estimators. |
| risk and evidence | verify_phase4, analysis schema, alerts and investigations | RiskThresholds, RiskWeights and EvidenceReason. Evidence carries category, feature, value, baseline and explanation. |
| analyzer | datasets, alerts, graph, investigations, analysis and verify_phase4 | get_analysis_paths, has_analysis_data, get_analysis_status and run_full_analysis. Return AnalysisSummary and AnalysisStatusResponse as defined in the existing schemas. |
| clustering | test_clustering, test_clustering_api and frontend/src/lib/api.ts | Expose the 22 clustering features, preprocessing, assignments, profiles, wallet lookup and similarity. Preserve the six-group seeded fixture, PCA coordinates and measured diagnostics. |
| persisted files | graph builder, alert and investigation endpoints | wallet_features.parquet, wallet_anomalies.parquet, investigative_leads.parquet and analysis_summary.json. Alert IDs and ranks must be stable for identical inputs. |
