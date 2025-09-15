#!/usr/bin/env python3
"""
GDPR/HIPAA Alias Data Importer
Imports comprehensive real-world alias data for GDPR and HIPAA regulations
This will significantly enhance the local coverage target of ≥95%
"""

import sys
import csv
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports  
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pii_scanner_poc.services.local_alias_database import alias_database, FieldAlias
    from pii_scanner_poc.models.data_models import PIIType, RiskLevel, Regulation
    print("✅ Alias database modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class RegulationAliasImporter:
    """Imports GDPR/HIPAA alias data into the local alias database"""
    
    def __init__(self):
        self.db = alias_database
        self.imported_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
        # PII Type mappings from the provided data
        self.pii_type_mappings = {
            # Identity and Personal Info
            'name': PIIType.NAME,
            'names': PIIType.NAME,
            'full name': PIIType.NAME,
            'first name': PIIType.NAME,
            'last name': PIIType.NAME,
            'surname': PIIType.NAME,
            'middle name': PIIType.NAME,
            'maiden name': PIIType.NAME,
            'nickname': PIIType.NAME,
            'family name': PIIType.NAME,
            'given name': PIIType.NAME,
            
            # Contact Information
            'email': PIIType.EMAIL,
            'email address': PIIType.EMAIL,
            'email addresses': PIIType.EMAIL,
            'personal email': PIIType.EMAIL,
            'electronic mail': PIIType.EMAIL,
            
            'phone': PIIType.PHONE,
            'telephone': PIIType.PHONE,
            'telephone numbers': PIIType.PHONE,
            'phone number': PIIType.PHONE,
            'mobile number': PIIType.PHONE,
            'landline number': PIIType.PHONE,
            'emergency contact': PIIType.PHONE,
            'fax': PIIType.PHONE,
            'fax numbers': PIIType.PHONE,
            
            # Location Information
            'address': PIIType.ADDRESS,
            'home address': PIIType.ADDRESS,
            'street address': PIIType.ADDRESS,
            'geographic subdivisions': PIIType.ADDRESS,
            'location data': PIIType.ADDRESS,
            'gps coordinates': PIIType.ADDRESS,
            'postal code': PIIType.ADDRESS,
            'zip code': PIIType.ADDRESS,
            'city': PIIType.ADDRESS,
            'state': PIIType.ADDRESS,
            'country': PIIType.ADDRESS,
            
            # Identification Numbers
            'ssn': PIIType.SSN,
            'social security': PIIType.SSN,
            'social security numbers': PIIType.SSN,
            'social security identifier': PIIType.SSN,
            
            # Financial Information
            'credit card': PIIType.FINANCIAL,
            'debit card': PIIType.FINANCIAL,
            'card number': PIIType.FINANCIAL,
            'bank account': PIIType.FINANCIAL,
            'iban': PIIType.FINANCIAL,
            'account numbers': PIIType.FINANCIAL,
            'billing information': PIIType.FINANCIAL,
            
            # Medical Information
            'medical': PIIType.MEDICAL,
            'health': PIIType.MEDICAL,
            'diagnosis': PIIType.MEDICAL,
            'treatment': PIIType.MEDICAL,
            'laboratory': PIIType.MEDICAL,
            'medication': PIIType.MEDICAL,
            'vital signs': PIIType.MEDICAL,
            'medical record': PIIType.MEDICAL,
            'health plan': PIIType.MEDICAL,
            'mental health': PIIType.MEDICAL,
            'genetic': PIIType.MEDICAL,
            'hiv': PIIType.MEDICAL,
            'reproductive health': PIIType.MEDICAL,
            
            # Identification Documents
            'driver': PIIType.ID,
            'license': PIIType.ID,
            'passport': PIIType.ID,
            'certificate': PIIType.ID,
            'national id': PIIType.ID,
            'employee id': PIIType.ID,
            
            # Biometric Data
            'biometric': PIIType.BIOMETRIC,
            'fingerprint': PIIType.BIOMETRIC,
            'facial': PIIType.BIOMETRIC,
            'voice': PIIType.BIOMETRIC,
            'iris': PIIType.BIOMETRIC,
            'retinal': PIIType.BIOMETRIC,
            'photograph': PIIType.BIOMETRIC,
            
            # Network/Technical
            'ip address': PIIType.NETWORK,
            'url': PIIType.NETWORK,
            'cookie': PIIType.NETWORK,
            'device identifier': PIIType.NETWORK,
            'advertising id': PIIType.NETWORK,
        }
    
    def map_pii_type(self, field_description: str) -> PIIType:
        """Map field description to PIIType enum"""
        field_lower = field_description.lower().strip()
        
        # Direct mapping
        for key, pii_type in self.pii_type_mappings.items():
            if key in field_lower:
                return pii_type
        
        # Default to OTHER if no match found
        return PIIType.OTHER
    
    def determine_risk_level(self, pii_type: PIIType, is_sensitive: bool = False) -> RiskLevel:
        """Determine risk level based on PII type and sensitivity"""
        if is_sensitive:
            return RiskLevel.HIGH
        
        high_risk_types = {PIIType.SSN, PIIType.MEDICAL, PIIType.FINANCIAL, PIIType.BIOMETRIC}
        medium_risk_types = {PIIType.EMAIL, PIIType.PHONE, PIIType.ADDRESS, PIIType.ID}
        
        if pii_type in high_risk_types:
            return RiskLevel.HIGH
        elif pii_type in medium_risk_types:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def import_hipaa_data(self):
        """Import HIPAA alias data"""
        print("\n📋 Importing HIPAA Alias Data...")
        
        # HIPAA data from the provided information
        hipaa_data = [
            # Names
            ("name", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Personal identifiers, Patient name"),
            ("personal_identifiers", "Names", PIIType.NAME, RiskLevel.MEDIUM, "First element in Safe Harbor method"),
            ("patient_name", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Patient identification"),
            ("first_name", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Given name"),
            ("middle_name", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Middle initial or name"),
            ("last_name", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Family name, surname"),
            ("maiden_name", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Previous family name"),
            ("nickname", "Names", PIIType.NAME, RiskLevel.MEDIUM, "Informal name"),
            
            # Geographic/Address Information
            ("street_address", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "Street address, city, county"),
            ("city", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "Municipal location"),
            ("county", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "County subdivision"),
            ("zip_code", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "Postal code"),
            ("postal_code", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "ZIP code equivalent"),
            ("precinct", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "Voting or district precinct"),
            ("location_data", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "Geographic location"),
            ("address_information", "Geographic subdivisions", PIIType.ADDRESS, RiskLevel.MEDIUM, "Complete address"),
            
            # Dates
            ("birth_date", "Birth date", PIIType.OTHER, RiskLevel.HIGH, "Date of birth; ages >89 aggregated"),
            ("dob", "Birth date", PIIType.OTHER, RiskLevel.HIGH, "Date of birth"),
            ("admission_date", "Admission date", PIIType.OTHER, RiskLevel.MEDIUM, "Hospital admission date"),
            ("discharge_date", "Discharge date", PIIType.OTHER, RiskLevel.MEDIUM, "Hospital discharge date"),
            ("death_date", "Date of death", PIIType.OTHER, RiskLevel.HIGH, "Date of individual's death"),
            ("procedure_date", "Procedure date", PIIType.MEDICAL, RiskLevel.MEDIUM, "Medical procedure date"),
            
            # Contact Information
            ("phone_number", "Telephone numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Any phone number"),
            ("home_phone", "Telephone numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Residential phone"),
            ("cell_phone", "Telephone numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Mobile phone"),
            ("work_phone", "Telephone numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Business phone"),
            ("emergency_contact", "Telephone numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Emergency contact number"),
            ("contact_information", "Telephone numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Contact details"),
            
            ("fax_number", "Fax numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Facsimile number"),
            ("personal_fax", "Fax numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Personal fax number"),
            ("work_fax", "Fax numbers", PIIType.PHONE, RiskLevel.MEDIUM, "Work fax number"),
            
            ("email_address", "Email addresses", PIIType.EMAIL, RiskLevel.MEDIUM, "Electronic mail address"),
            ("personal_email", "Email addresses", PIIType.EMAIL, RiskLevel.MEDIUM, "Personal email"),
            ("work_email", "Email addresses", PIIType.EMAIL, RiskLevel.MEDIUM, "Work email"),
            ("electronic_mail", "Email addresses", PIIType.EMAIL, RiskLevel.MEDIUM, "Email contact"),
            
            # Identification Numbers
            ("ssn", "Social Security Numbers", PIIType.SSN, RiskLevel.HIGH, "9-digit SSA identifier"),
            ("social_security_number", "Social Security Numbers", PIIType.SSN, RiskLevel.HIGH, "Social Security identifier"),
            ("social_security_identifier", "Social Security Numbers", PIIType.SSN, RiskLevel.HIGH, "SSN identifier"),
            
            # Medical Records
            ("mrn", "Medical record numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Medical record number"),
            ("medical_record_number", "Medical record numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Provider patient ID"),
            ("patient_id", "Medical record numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Patient identifier"),
            ("chart_number", "Medical record numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Medical chart ID"),
            ("hospital_mrn", "Medical record numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Hospital medical record"),
            ("clinic_mrn", "Medical record numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Clinic medical record"),
            
            # Health Plan Information
            ("insurance_id", "Health plan beneficiary numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Insurance identifier"),
            ("member_id", "Health plan beneficiary numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Health plan member ID"),
            ("beneficiary_id", "Health plan beneficiary numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Benefits ID"),
            ("medicare_number", "Health plan beneficiary numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Medicare beneficiary number"),
            ("medicaid_id", "Health plan beneficiary numbers", PIIType.MEDICAL, RiskLevel.HIGH, "Medicaid identifier"),
            
            # Financial Accounts
            ("account_number", "Account numbers", PIIType.FINANCIAL, RiskLevel.HIGH, "Financial account number"),
            ("patient_account", "Account numbers", PIIType.FINANCIAL, RiskLevel.HIGH, "Hospital patient account"),
            ("billing_account", "Account numbers", PIIType.FINANCIAL, RiskLevel.HIGH, "Billing account number"),
            
            # Licenses and Certificates
            ("license_number", "Certificate/license numbers", PIIType.ID, RiskLevel.MEDIUM, "License identifier"),
            ("drivers_license", "Certificate/license numbers", PIIType.ID, RiskLevel.MEDIUM, "Driver's license number"),
            ("state_id", "Certificate/license numbers", PIIType.ID, RiskLevel.MEDIUM, "State identification"),
            ("certification_number", "Certificate/license numbers", PIIType.ID, RiskLevel.MEDIUM, "Certification ID"),
            ("medical_license", "Certificate/license numbers", PIIType.ID, RiskLevel.MEDIUM, "Medical license number"),
            
            # Vehicle Information
            ("license_plate", "Vehicle identifiers", PIIType.ID, RiskLevel.LOW, "Vehicle license plate"),
            ("vin", "Vehicle identifiers", PIIType.ID, RiskLevel.LOW, "Vehicle identification number"),
            ("vehicle_id", "Vehicle identifiers", PIIType.ID, RiskLevel.LOW, "Auto identifier"),
            
            # Device Information
            ("device_serial", "Device identifiers", PIIType.OTHER, RiskLevel.MEDIUM, "Medical device serial"),
            ("implant_serial", "Device identifiers", PIIType.MEDICAL, RiskLevel.HIGH, "Implanted device serial"),
            ("equipment_id", "Device identifiers", PIIType.OTHER, RiskLevel.MEDIUM, "Medical equipment ID"),
            
            # Network Information
            ("url", "Web URLs", PIIType.NETWORK, RiskLevel.MEDIUM, "Web address"),
            ("patient_portal_url", "Web URLs", PIIType.NETWORK, RiskLevel.MEDIUM, "Patient portal address"),
            ("personal_webpage", "Web URLs", PIIType.NETWORK, RiskLevel.MEDIUM, "Personal web address"),
            
            ("ip_address", "IP addresses", PIIType.NETWORK, RiskLevel.MEDIUM, "Internet Protocol address"),
            ("ipv4_address", "IP addresses", PIIType.NETWORK, RiskLevel.MEDIUM, "IPv4 address"),
            ("ipv6_address", "IP addresses", PIIType.NETWORK, RiskLevel.MEDIUM, "IPv6 address"),
            
            # Biometric Information
            ("fingerprint", "Biometric identifiers", PIIType.BIOMETRIC, RiskLevel.HIGH, "Fingerprint data"),
            ("voiceprint", "Biometric identifiers", PIIType.BIOMETRIC, RiskLevel.HIGH, "Voice pattern"),
            ("retinal_scan", "Biometric identifiers", PIIType.BIOMETRIC, RiskLevel.HIGH, "Retinal image"),
            ("hand_geometry", "Biometric identifiers", PIIType.BIOMETRIC, RiskLevel.HIGH, "Hand measurement"),
            
            # Photos and Images
            ("patient_photo", "Photographic images", PIIType.BIOMETRIC, RiskLevel.HIGH, "Patient photograph"),
            ("id_badge_photo", "Photographic images", PIIType.BIOMETRIC, RiskLevel.HIGH, "ID photograph"),
            ("clinical_photo", "Photographic images", PIIType.BIOMETRIC, RiskLevel.HIGH, "Clinical image"),
            
            # Medical Information
            ("diagnosis", "Diagnosis information", PIIType.MEDICAL, RiskLevel.HIGH, "Medical diagnosis"),
            ("medical_condition", "Diagnosis information", PIIType.MEDICAL, RiskLevel.HIGH, "Health condition"),
            ("health_condition", "Diagnosis information", PIIType.MEDICAL, RiskLevel.HIGH, "Medical diagnosis"),
            ("icd_code", "Diagnosis information", PIIType.MEDICAL, RiskLevel.HIGH, "Diagnosis code"),
            
            ("treatment", "Treatment information", PIIType.MEDICAL, RiskLevel.HIGH, "Medical treatment"),
            ("procedure", "Treatment information", PIIType.MEDICAL, RiskLevel.HIGH, "Medical procedure"),
            ("surgery", "Treatment information", PIIType.MEDICAL, RiskLevel.HIGH, "Surgical procedure"),
            ("therapy", "Treatment information", PIIType.MEDICAL, RiskLevel.HIGH, "Therapeutic treatment"),
            
            ("lab_result", "Laboratory results", PIIType.MEDICAL, RiskLevel.HIGH, "Laboratory test result"),
            ("blood_test", "Laboratory results", PIIType.MEDICAL, RiskLevel.HIGH, "Blood test result"),
            ("urine_test", "Laboratory results", PIIType.MEDICAL, RiskLevel.HIGH, "Urine test result"),
            ("genetic_test", "Laboratory results", PIIType.MEDICAL, RiskLevel.HIGH, "Genetic test result"),
            
            ("vital_signs", "Vital signs", PIIType.MEDICAL, RiskLevel.MEDIUM, "Body function measurements"),
            ("blood_pressure", "Vital signs", PIIType.MEDICAL, RiskLevel.MEDIUM, "Blood pressure reading"),
            ("heart_rate", "Vital signs", PIIType.MEDICAL, RiskLevel.MEDIUM, "Heart rate measurement"),
            ("temperature", "Vital signs", PIIType.MEDICAL, RiskLevel.MEDIUM, "Body temperature"),
            ("oxygen_level", "Vital signs", PIIType.MEDICAL, RiskLevel.MEDIUM, "Oxygen saturation"),
            
            ("medication", "Medication information", PIIType.MEDICAL, RiskLevel.HIGH, "Prescription medication"),
            ("prescription", "Medication information", PIIType.MEDICAL, RiskLevel.HIGH, "Prescribed drug"),
            ("dosage", "Medication information", PIIType.MEDICAL, RiskLevel.HIGH, "Medication dosage"),
            ("drug_allergy", "Medication information", PIIType.MEDICAL, RiskLevel.HIGH, "Drug allergies"),
        ]
        
        for alias_name, standard_name, pii_type, risk_level, description in hipaa_data:
            self._add_alias(
                alias_name=alias_name,
                standard_field_name=standard_name.lower().replace(' ', '_'),
                pii_type=pii_type,
                risk_level=risk_level,
                applicable_regulations=[Regulation.HIPAA],
                confidence_score=0.9,
                created_by="hipaa_importer",
                validation_status="approved",
                rationale=f"HIPAA Safe Harbor identifier: {description}"
            )
    
    def import_gdpr_data(self):
        """Import GDPR alias data"""
        print("\n📋 Importing GDPR Alias Data...")
        
        # GDPR Personal Data
        gdpr_personal_data = [
            # Basic Personal Information
            ("full_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("first_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("middle_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("surname", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("last_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("family_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("given_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("suffix", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("prefix", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            ("maiden_name", "name", PIIType.NAME, RiskLevel.MEDIUM, False),
            
            ("gender", "personal_data", PIIType.OTHER, RiskLevel.LOW, False),
            ("sex", "personal_data", PIIType.OTHER, RiskLevel.LOW, False),
            
            # Contact Information
            ("phone_number", "contact", PIIType.PHONE, RiskLevel.MEDIUM, False),
            ("emergency_contact_number", "contact", PIIType.PHONE, RiskLevel.MEDIUM, False),
            ("mobile_number", "contact", PIIType.PHONE, RiskLevel.MEDIUM, False),
            ("landline_number", "contact", PIIType.PHONE, RiskLevel.MEDIUM, False),
            ("telephone_number", "contact", PIIType.PHONE, RiskLevel.MEDIUM, False),
            
            ("email_address", "contact", PIIType.EMAIL, RiskLevel.MEDIUM, False),
            ("personal_email", "contact", PIIType.EMAIL, RiskLevel.MEDIUM, False),
            ("email", "contact", PIIType.EMAIL, RiskLevel.MEDIUM, False),
            
            # Address Information
            ("home_address", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("street_address", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("postal_code", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("zip_code", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("latitude", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("longitude", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("full_address", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("address", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("landmark", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("city", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("state", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("country", "address", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            
            # Date Information
            ("date_of_birth", "personal", PIIType.OTHER, RiskLevel.HIGH, False),
            ("dob", "personal", PIIType.OTHER, RiskLevel.HIGH, False),
            ("birthdate", "personal", PIIType.OTHER, RiskLevel.HIGH, False),
            
            # Financial Information
            ("credit_card_number", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("ccn", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("cc_number", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("debit_card_number", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("bank_card_number", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("cardholder_name", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("authorized_user_name", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("card_name", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("cvv", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("card_verification_value", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("cvc", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("card_expiry_date", "financial", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            
            # Identity Documents
            ("national_id", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("nid", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("national_identifier", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("uid", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("vid", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("ssn", "identification", PIIType.SSN, RiskLevel.HIGH, False),
            ("social_security_identifier", "identification", PIIType.SSN, RiskLevel.HIGH, False),
            ("drivers_license_number", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("license_number", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("dl_id", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("passport_number", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("national_passport_number", "identification", PIIType.ID, RiskLevel.HIGH, False),
            ("passport_id", "identification", PIIType.ID, RiskLevel.HIGH, False),
            
            # Financial Account Information
            ("iban", "financial_account", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("bank_account_number", "financial_account", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("account_number", "financial_account", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("tax_identification_number", "financial_account", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("personal_account_number", "financial_account", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            ("pan_number", "financial_account", PIIType.FINANCIAL, RiskLevel.HIGH, False),
            
            # Employment Information
            ("employee_number", "employment", PIIType.ID, RiskLevel.MEDIUM, False),
            ("staff_id", "employment", PIIType.ID, RiskLevel.MEDIUM, False),
            ("employee_code", "employment", PIIType.ID, RiskLevel.MEDIUM, False),
            ("marital_status", "personal", PIIType.OTHER, RiskLevel.LOW, False),
            ("relationship_status", "personal", PIIType.OTHER, RiskLevel.LOW, False),
            
            # Digital Identifiers
            ("gps_coordinates", "location", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("google_location", "location", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("location", "location", PIIType.ADDRESS, RiskLevel.MEDIUM, False),
            ("ip_address", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("user_ip_address", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("mobile_advertising_id", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("advertising_id", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("idfa", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("aaid", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("gaid", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("cookie_identifier", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            ("cookie_id", "network", PIIType.NETWORK, RiskLevel.MEDIUM, False),
            
            # Free text and Comments
            ("free_text_comment", "user_input", PIIType.OTHER, RiskLevel.MEDIUM, False),
            ("user_comment", "user_input", PIIType.OTHER, RiskLevel.MEDIUM, False),
            ("comment", "user_input", PIIType.OTHER, RiskLevel.MEDIUM, False),
            
            # Signatures
            ("signature", "identification", PIIType.BIOMETRIC, RiskLevel.HIGH, False),
            ("digital_signature", "identification", PIIType.BIOMETRIC, RiskLevel.HIGH, False),
            ("electronic_signature", "identification", PIIType.BIOMETRIC, RiskLevel.HIGH, False),
            ("biometric_signature", "identification", PIIType.BIOMETRIC, RiskLevel.HIGH, False),
        ]
        
        # GDPR Sensitive/Special Category Data
        gdpr_sensitive_data = [
            # Biometric Data
            ("fingerprint_data", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("facial_recognition_data", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("iris_scan", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("retina_scan", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("voiceprint_data", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("facial_image", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("voice_data", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            ("fingerprints", "biometric", PIIType.BIOMETRIC, RiskLevel.HIGH, True),
            
            # Political Information
            ("political_opinion", "political", PIIType.OTHER, RiskLevel.HIGH, True),
            ("political_belief", "political", PIIType.OTHER, RiskLevel.HIGH, True),
            ("political_party_affiliation", "political", PIIType.OTHER, RiskLevel.HIGH, True),
            ("voting_history", "political", PIIType.OTHER, RiskLevel.HIGH, True),
            ("political_donations", "political", PIIType.OTHER, RiskLevel.HIGH, True),
            ("political_survey_responses", "political", PIIType.OTHER, RiskLevel.HIGH, True),
            
            # Religious/Philosophical Beliefs
            ("religion", "beliefs", PIIType.OTHER, RiskLevel.HIGH, True),
            ("religious_affiliation", "beliefs", PIIType.OTHER, RiskLevel.HIGH, True),
            ("philosophical_belief", "beliefs", PIIType.OTHER, RiskLevel.HIGH, True),
            ("religious_beliefs", "beliefs", PIIType.OTHER, RiskLevel.HIGH, True),
            
            # Cultural/Social Identity
            ("language", "cultural", PIIType.OTHER, RiskLevel.MEDIUM, True),
            ("cultural_identity", "cultural", PIIType.OTHER, RiskLevel.HIGH, True),
            ("social_identity", "cultural", PIIType.OTHER, RiskLevel.HIGH, True),
            
            # Genetic Data
            ("genetic_sequencing_data", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("genetic_information", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("dna_tests", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("dna_sequence", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("carrier_status", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("paternity_results", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("familial_match_results", "genetic", PIIType.MEDICAL, RiskLevel.HIGH, True),
            
            # Trade Union
            ("trade_union_membership", "union", PIIType.OTHER, RiskLevel.HIGH, True),
            ("union_membership", "union", PIIType.OTHER, RiskLevel.HIGH, True),
            
            # Racial/Ethnic Origin
            ("ethnic_group", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            ("ethnic_origin", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            ("race", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            ("racial_origin", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            ("caste", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            ("subcaste", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            ("ethnicity", "ethnicity", PIIType.OTHER, RiskLevel.HIGH, True),
            
            # Health Data
            ("medical_condition", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("medical_reports", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("health_status", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("health_information", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("treatment_history", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("medication_history", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("mental_health_data", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("psychiatric_data", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            ("health_data", "health", PIIType.MEDICAL, RiskLevel.HIGH, True),
            
            # Sex Life and Sexual Orientation
            ("sexual_orientation", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("relationship_type", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("preferred_partners", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("preferred_gender", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("dating_app_data", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("partner_history", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("sexual_partner_history", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("sexual_health_data", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            ("sex_life_data", "sexuality", PIIType.OTHER, RiskLevel.HIGH, True),
            
            # Criminal Data
            ("crime", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
            ("offense", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
            ("sanction", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
            ("penalty", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
            ("criminal_history", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
            ("criminal_proceedings", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
            ("administrative_proceedings", "criminal", PIIType.OTHER, RiskLevel.HIGH, True),
        ]
        
        # Import personal data
        for alias_name, category, pii_type, risk_level, is_sensitive in gdpr_personal_data:
            regulation = [Regulation.GDPR]
            if is_sensitive:
                regulation.append(Regulation.CCPA)  # Often applies to sensitive data as well
                
            self._add_alias(
                alias_name=alias_name,
                standard_field_name=category,
                pii_type=pii_type,
                risk_level=risk_level,
                applicable_regulations=regulation,
                confidence_score=0.9,
                created_by="gdpr_importer", 
                validation_status="approved",
                rationale=f"GDPR personal data: {category}"
            )
        
        # Import sensitive data
        for alias_name, category, pii_type, risk_level, is_sensitive in gdpr_sensitive_data:
            self._add_alias(
                alias_name=alias_name,
                standard_field_name=category,
                pii_type=pii_type,
                risk_level=risk_level,
                applicable_regulations=[Regulation.GDPR],
                confidence_score=0.95,  # Higher confidence for sensitive data
                created_by="gdpr_sensitive_importer",
                validation_status="approved",
                rationale=f"GDPR special category data: {category}"
            )
    
    def import_common_aliases(self):
        """Import common field name aliases from the provided data"""
        print("\n📋 Importing Common Field Aliases...")
        
        # Common aliases from the comprehensive list provided
        common_aliases = [
            # Email variations
            ("cust_email", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("customer_email", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("user_email", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("contact_email", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("primary_email", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("email_addr", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("e_mail", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            ("mail", "email", PIIType.EMAIL, RiskLevel.MEDIUM),
            
            # Phone variations
            ("cust_phone", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("customer_phone", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("phone_num", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("phone_no", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("contact_phone", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("tel", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("telephone", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("mobile", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("cell", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            ("cellphone", "phone", PIIType.PHONE, RiskLevel.MEDIUM),
            
            # Name variations
            ("cust_name", "name", PIIType.NAME, RiskLevel.MEDIUM),
            ("customer_name", "name", PIIType.NAME, RiskLevel.MEDIUM),
            ("user_name", "name", PIIType.NAME, RiskLevel.MEDIUM),
            ("full_name", "name", PIIType.NAME, RiskLevel.MEDIUM),
            ("fname", "first_name", PIIType.NAME, RiskLevel.MEDIUM),
            ("lname", "last_name", PIIType.NAME, RiskLevel.MEDIUM),
            ("firstname", "first_name", PIIType.NAME, RiskLevel.MEDIUM),
            ("lastname", "last_name", PIIType.NAME, RiskLevel.MEDIUM),
            ("f_name", "first_name", PIIType.NAME, RiskLevel.MEDIUM),
            ("l_name", "last_name", PIIType.NAME, RiskLevel.MEDIUM),
            
            # Address variations
            ("cust_address", "address", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("customer_address", "address", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("street_addr", "address", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("addr", "address", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("address1", "address", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("address2", "address", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("zip", "postal_code", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("zipcode", "postal_code", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("postcode", "postal_code", PIIType.ADDRESS, RiskLevel.MEDIUM),
            ("postal", "postal_code", PIIType.ADDRESS, RiskLevel.MEDIUM),
            
            # SSN variations
            ("social_security", "ssn", PIIType.SSN, RiskLevel.HIGH),
            ("ssn", "ssn", PIIType.SSN, RiskLevel.HIGH),
            ("ss_number", "ssn", PIIType.SSN, RiskLevel.HIGH),
            ("social_sec", "ssn", PIIType.SSN, RiskLevel.HIGH),
            ("soc_sec_num", "ssn", PIIType.SSN, RiskLevel.HIGH),
            
            # Medical variations
            ("patient_id", "medical_record", PIIType.MEDICAL, RiskLevel.HIGH),
            ("mrn", "medical_record", PIIType.MEDICAL, RiskLevel.HIGH),
            ("medical_id", "medical_record", PIIType.MEDICAL, RiskLevel.HIGH),
            ("health_id", "medical_record", PIIType.MEDICAL, RiskLevel.HIGH),
            ("patient_number", "medical_record", PIIType.MEDICAL, RiskLevel.HIGH),
            
            # Financial variations  
            ("account_num", "account_number", PIIType.FINANCIAL, RiskLevel.HIGH),
            ("acct_num", "account_number", PIIType.FINANCIAL, RiskLevel.HIGH),
            ("account_no", "account_number", PIIType.FINANCIAL, RiskLevel.HIGH),
            ("card_num", "card_number", PIIType.FINANCIAL, RiskLevel.HIGH),
            ("card_no", "card_number", PIIType.FINANCIAL, RiskLevel.HIGH),
            ("cc_num", "credit_card", PIIType.FINANCIAL, RiskLevel.HIGH),
            ("credit_card_num", "credit_card", PIIType.FINANCIAL, RiskLevel.HIGH),
            
            # ID variations
            ("emp_id", "employee_id", PIIType.ID, RiskLevel.MEDIUM),
            ("employee_num", "employee_id", PIIType.ID, RiskLevel.MEDIUM),
            ("staff_num", "employee_id", PIIType.ID, RiskLevel.MEDIUM),
            ("badge_id", "employee_id", PIIType.ID, RiskLevel.MEDIUM),
            ("worker_id", "employee_id", PIIType.ID, RiskLevel.MEDIUM),
        ]
        
        for alias_name, standard_name, pii_type, risk_level in common_aliases:
            self._add_alias(
                alias_name=alias_name,
                standard_field_name=standard_name,
                pii_type=pii_type,
                risk_level=risk_level,
                applicable_regulations=[Regulation.GDPR, Regulation.HIPAA],
                confidence_score=0.85,
                created_by="common_alias_importer",
                validation_status="approved",
                rationale="Common field naming pattern"
            )
    
    def _add_alias(self, alias_name: str, standard_field_name: str, pii_type: PIIType,
                   risk_level: RiskLevel, applicable_regulations: List[Regulation],
                   confidence_score: float, created_by: str, validation_status: str,
                   rationale: str):
        """Helper method to add an alias to the database"""
        try:
            # Generate alias ID
            alias_id = hashlib.md5(f"{alias_name}_{pii_type.value}_{created_by}".encode()).hexdigest()[:16]
            
            alias = FieldAlias(
                alias_id=alias_id,
                standard_field_name=standard_field_name,
                alias_name=alias_name.lower(),
                confidence_score=confidence_score,
                pii_type=pii_type,
                risk_level=risk_level,
                applicable_regulations=applicable_regulations,
                validation_status=validation_status,
                created_by=created_by
            )
            
            if self.db.add_field_alias(alias):
                self.imported_count += 1
                if self.imported_count % 50 == 0:
                    print(f"   Imported {self.imported_count} aliases...")
            else:
                self.skipped_count += 1
                
        except Exception as e:
            self.error_count += 1
            if self.error_count <= 5:  # Only show first 5 errors
                print(f"   ⚠️ Error adding alias '{alias_name}': {e}")
    
    def run_import(self):
        """Run complete import process"""
        print("🚀 Starting Comprehensive GDPR/HIPAA Alias Import")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Import HIPAA data
            self.import_hipaa_data()
            
            # Import GDPR data
            self.import_gdpr_data()
            
            # Import common aliases
            self.import_common_aliases()
            
            # Get final statistics
            stats = self.db.get_performance_statistics()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n✅ IMPORT COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"📊 Import Results:")
            print(f"   ✅ Imported: {self.imported_count}")
            print(f"   ⚠️ Skipped: {self.skipped_count}")
            print(f"   ❌ Errors: {self.error_count}")
            print(f"   ⏱️ Duration: {duration:.2f} seconds")
            
            print(f"\n📋 Database Statistics:")
            print(f"   Total Aliases: {stats['aliases']['total_aliases']}")
            print(f"   Approved Aliases: {stats['aliases']['approved_aliases']}")
            print(f"   Average Confidence: {stats['aliases']['avg_confidence']:.3f}")
            
            # Show sample aliases
            print(f"\n🔍 Sample Imported Aliases:")
            sample_aliases = self.db.export_aliases(validation_status="approved")[:10]
            for alias in sample_aliases:
                print(f"   {alias['alias_name']} -> {alias['pii_type']} ({alias['confidence_score']:.2f})")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Import failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main execution function"""
    print("🏛️ GDPR/HIPAA Alias Database Importer")
    print("Importing comprehensive real-world alias data for enhanced PII detection")
    print()
    
    try:
        importer = RegulationAliasImporter()
        success = importer.run_import()
        
        if success:
            print("\n🎉 Import completed successfully!")
            print("The alias database now contains comprehensive GDPR and HIPAA patterns.")
            print("This should significantly improve the ≥95% local coverage target.")
            return 0
        else:
            print("\n❌ Import failed. Check the error messages above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Import cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())