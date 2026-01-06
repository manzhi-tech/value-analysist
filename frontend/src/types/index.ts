export interface AnalysisSession {
    id: string; // Corrected from 'str'
    created_at: string;
    file_path: string;
    file_name: string;
    file_paths?: string[];
    company_name?: string;

    // Results
    business_analysis_result?: string;
    mda_analysis_result?: string;
    financial_analysis_result?: string;
    competitor_analysis_result?: string;
    valuation_result?: string;

    // Statuses
    business_status?: string;
    mda_status?: string;
    financial_status?: string;
    competitor_status?: string;
    valuation_status?: string;
}

export type AnalysisStep = 'upload' | 'business' | 'mda' | 'financial' | 'competitor' | 'valuation';

export interface Citation {
    page: number;
    rect?: [number, number, number, number]; // x, y, w, h usually
    source_id?: string;
}
