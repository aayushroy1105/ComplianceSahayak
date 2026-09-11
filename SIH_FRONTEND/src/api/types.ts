export interface OfficerProfile {
  officer_id: string;
  badge_number: string | null;
  department: string | null;
  jurisdiction: string | null;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: 'USER' | 'OFFICER' | 'ADMIN';
  created_at: string;
  officer_profile: OfficerProfile | null;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface ApiError {
  detail?: string;
  message?: string;
}

export interface InspectionCreateRequest {
  latitude?: number | null;
  longitude?: number | null;
  location_text?: string | null;
  inspection_date?: string | null;
  officer_notes?: string | null;
  product_id?: string | null;
  manufacturer_id?: string | null;
}

export interface InspectionImageResponse {
  id: string;
  image_type: string;
  original_filename: string | null;
  mime_type: string;
  file_size: number;
  uploaded_at: string;
}

export interface DeclarationResponse {
  id: string;
  field_name: string;
  raw_value: string | null;
  normalized_value: string | number | null;
  normalized_unit: string | null;
  confidence: number;
  extraction_status: string;
  bounding_box: number[] | null;
}

export interface CorrectiveActionResponse {
  id: string;
  violation_reference: string;
  action_text: string;
  status: string;
}

export interface ViolationResponse {
  id: string;
  violation_code: string;
  rule_id: string;
  rule_version: string | null;
  severity: string | null;
  description: string;
  confidence: number | null;
  evidence_references: string[];
  status: string;
  corrective_actions?: CorrectiveActionResponse[];
}

export interface EvidenceResponse {
  id: string;
  evidence_id_ai: string;
  evidence_type: string;
  ocr_text: string | null;
  bounding_box: number[] | null;
  declaration_reference: string | null;
  rule_id: string | null;
  description: string | null;
}

export interface InspectionCreateResponse {
  id: string;
  inspection_code: string;
  processing_status: string;
  compliance_status: string | null;
  review_status: string;
  image: InspectionImageResponse | null;
  latitude: number | null;
  longitude: number | null;
  location_text: string | null;
  created_at: string;
}

export interface InspectionDetailResponse {
  id: string;
  inspection_code: string;
  processing_status: string;
  compliance_status: string | null;
  review_status: string;
  review_required: boolean | null;
  review_reason: string | null;
  latitude: number | null;
  longitude: number | null;
  location_text: string | null;
  inspection_date: string | null;
  created_at: string;
  updated_at: string;
  product_name_ai?: string | null;
  product_category_ai?: string | null;
  signals?: string[] | null;
  classification_method?: string | null;
  images: InspectionImageResponse[];
  declarations: DeclarationResponse[];
  violations: ViolationResponse[];
  evidence: EvidenceResponse[];
}

export interface Pagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface InspectionListItem {
  id: string;
  inspection_code: string;
  processing_status: string;
  compliance_status: string | null;
  review_status: string;
  product_name_ai?: string | null;
  product_category_ai?: string | null;
  signals?: string[] | null;
  classification_method?: string | null;
  manufacturer_name?: string | null;
  violation_count: number;
  latitude: number | null;
  longitude: number | null;
  location_text: string | null;
  inspection_date: string | null;
  created_at: string;
}

export interface InspectionListResponse {
  items: InspectionListItem[];
  pagination: Pagination;
}

export interface LocationMarker {
  inspection_id: string;
  latitude: number;
  longitude: number;
  inspection_date: string | null;
  manufacturer: string | null;
  compliance_status: string | null;
  processing_status: string;
}

export interface LocationMarkersResponse {
  items: LocationMarker[];
  pagination: Pagination;
}

export interface ProductResponse {
  id: string;
  product_name: string;
  category: string | null;
  created_at: string;
}

export interface ManufacturerResponse {
  id: string;
  name: string;
  normalized_name: string;
  created_at: string;
  updated_at: string;
}

export interface ManufacturerListResponse {
  items: ManufacturerResponse[];
  pagination: Pagination;
}

export interface ManufacturerDetailResponse {
  id: string;
  name: string;
  normalized_name: string;
  created_at: string;
  updated_at: string;
  products: ProductResponse[];
}

export interface ManufacturerHistoryItem {
  id: string;
  inspection_code: string;
  inspection_date: string | null;
  processing_status: string;
  compliance_status: string | null;
  product_name_ai: string | null;
  violation_count: number;
  created_at: string;
}

export interface ManufacturerHistoryResponse {
  items: ManufacturerHistoryItem[];
  pagination: Pagination;
}

export interface ManufacturerAnalytics {
  manufacturer_id: string;
  manufacturer_name: string;
  total_inspections: number;
  total_violations: number;
  repeat_violation_count: number;
  top_violation_codes: string[];
  latest_inspection: string | null;
  compliance_summary: string;
}

export interface AnalyticsRepeatOffendersResponse {
  offenders: ManufacturerAnalytics[];
}

export interface ReportResponse {
  id: string;
  inspection_id: string;
  report_path: string;
  report_type: string;
  version: number;
  generated_by: string | null;
  generated_at: string;
}
