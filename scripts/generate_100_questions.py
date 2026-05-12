"""
Generate 100 clinical trial questions (50 general, 50 emergency) based on the 12 PDFs.
Questions are directly answerable from the paper content.
"""

questions = [
    # ===== GENERAL QUESTIONS (801-850) =====
    # PMC1236923 - Cardiology: Heart failure guidelines in Europe
    (801, "general", "[PMC1236923] According to PMC1236923, how many national heart failure guidelines published after 1994 were analyzed in relation to the ESC guideline?"),
    (802, "general", "[PMC1236923] According to PMC1236923, in the IMPROVEMENT-HF study, what was the range of beta-blocker use in primary care across European countries?"),
    (803, "general", "[PMC1236923] According to PMC1236923, in which drug classes were relevant differences in heart failure treatment recommendations seen among European guidelines?"),
    (804, "general", "[PMC1236923] According to PMC1236923, what was the range of ACE inhibitor use in primary care across European countries in the IMPROVEMENT-HF study?"),
    (805, "general", "[PMC1236923] According to PMC1236923, what was the conclusion regarding differences in guideline recommendations and variation in prescribing among European countries?"),

    # PMC11846407 - Emergency: Sepsis infection management guidelines quality
    (806, "general", "[PMC11846407] According to PMC11846407, how many guidelines for the management of sepsis infection were identified in the systematic review?"),
    (807, "general", "[PMC11846407] According to PMC11846407, what was the range of overall scores for the included sepsis management guidelines using the AGREE II tool?"),
    (808, "general", "[PMC11846407] According to PMC11846407, which domain of the AGREE II assessment had the lowest average score among sepsis guidelines, and what was that score?"),
    (809, "general", "[PMC11846407] According to PMC11846407, what percentage of sepsis guideline recommendations were classified as weak strength?"),
    (810, "general", "[PMC11846407] According to PMC11846407, what percentage of evidence cited in sepsis guidelines was classified as very low quality?"),

    # PMC2898118 - Endocrinology: Patient preferences for diabetes care managers
    (811, "general", "[PMC2898118] According to PMC2898118, what percentage of patients responded to the survey about diabetes care manager preferences at Mayo Clinic?"),
    (812, "general", "[PMC2898118] According to PMC2898118, what percentage of providers expressed willingness to have various aspects of diabetes care managed by a care manager?"),
    (813, "general", "[PMC2898118] According to PMC2898118, what percentage of providers would be comfortable expanding the care manager role to other chronic diseases?"),
    (814, "general", "[PMC2898118] According to PMC2898118, what percentage of patient responders would be willing to see a care manager for other chronic problems beyond diabetes?"),
    (815, "general", "[PMC2898118] According to PMC2898118, what factor was associated with decreased patient likelihood to work with a care manager?"),

    # PMC12400259 - Gastroenterology: Role of dietitian in IBD
    (816, "general", "[PMC12400259] According to PMC12400259, what are the four main roles of nutrition and dietary treatments in inflammatory bowel disease management?"),
    (817, "general", "[PMC12400259] According to PMC12400259, why are dietitians identified as the most appropriate health professional for nutritional assessment in IBD patients?"),
    (818, "general", "[PMC12400259] According to PMC12400259, what do best practice IBD management guidelines recommend regarding multidisciplinary care models?"),
    (819, "general", "[PMC12400259] According to PMC12400259, what is the main barrier patients face in accessing nutrition-based strategies for IBD management?"),
    (820, "general", "[PMC12400259] According to PMC12400259, what outcome improvements have been shown when IBD multidisciplinary teams include dietitians?"),

    # PMC11638529 - Infectious disease: Antimicrobial stewardship in UK nursing students
    (821, "general", "[PMC11638529] According to PMC11638529, how many student nurses responded to the national survey on antimicrobial stewardship knowledge across UK universities?"),
    (822, "general", "[PMC11638529] According to PMC11638529, in which competency areas did student nurses feel least prepared regarding antimicrobial stewardship?"),
    (823, "general", "[PMC11638529] According to PMC11638529, what were the preferred modes of education delivery identified by student nurses for antimicrobial stewardship?"),
    (824, "general", "[PMC11638529] According to PMC11638529, what benefits did students who had shared antimicrobial stewardship teaching with other professions report?"),
    (825, "general", "[PMC11638529] According to PMC11638529, what knowledge gaps were identified in pre-registration nurse education regarding antimicrobial management?"),

    # PMC3701497 - Nephrology: Suboptimal BP control in CKD stage 3
    (826, "general", "[PMC3701497] According to PMC3701497, what was the prevalence of hypertension among CKD stage 3 patients in the Renal Risk in Derby Study?"),
    (827, "general", "[PMC3701497] According to PMC3701497, what percentage of hypertensive CKD stage 3 patients achieved NICE blood pressure targets?"),
    (828, "general", "[PMC3701497] According to PMC3701497, what percentage of hypertensive CKD stage 3 patients achieved KDOQI blood pressure targets?"),
    (829, "general", "[PMC3701497] According to PMC3701497, what percentage of CKD stage 3 patients with hypertension were only taking one antihypertensive agent?"),
    (830, "general", "[PMC3701497] According to PMC3701497, which patient characteristics were negatively associated with achieving BP control targets on multivariable analysis?"),

    # PMC10640530 - Neurology: Cerebral blood flow enhancers in acute ischemic stroke
    (831, "general", "[PMC10640530] According to PMC10640530, what five promising cerebral blood flow-enhancing therapeutics were identified for acute ischemic stroke?"),
    (832, "general", "[PMC10640530] According to PMC10640530, why are adjunctive therapies for cerebral blood flow enhancement urgently needed in acute ischemic stroke?"),
    (833, "general", "[PMC10640530] According to PMC10640530, what role does collateral blood flow play in the success of endovascular therapies for acute ischemic stroke?"),
    (834, "general", "[PMC10640530] According to PMC10640530, what is the mechanism of action of Fasudil as a cerebral blood flow enhancer in ischemic stroke?"),
    (835, "general", "[PMC10640530] According to PMC10640530, what is the role of the sphenopalatine ganglion stimulation as a potential CBF-enhancing therapy in acute ischemic stroke?"),

    # PMC4451740 - Obstetrics: MgSO4 use in pre-eclampsia in Nigeria
    (836, "general", "[PMC4451740] According to PMC4451740, what percentage of health facility providers correctly identified magnesium sulphate as the drug of choice for severe pre-eclampsia/eclampsia?"),
    (837, "general", "[PMC4451740] According to PMC4451740, what percentage of providers had been trained on the use of magnesium sulphate for pre-eclampsia/eclampsia management?"),
    (838, "general", "[PMC4451740] According to PMC4451740, what percentage of respondents indicated that magnesium sulphate was actually used in their facilities to prevent and treat convulsions?"),
    (839, "general", "[PMC4451740] According to PMC4451740, what were the main barriers to management of pre-eclampsia/eclampsia in health facilities in Northern Nigeria?"),
    (840, "general", "[PMC4451740] According to PMC4451740, what percentage of health facilities had service registers available for pre-eclampsia/eclampsia management?"),

    # PMC5803577 - Oncology: Publication proportions for breast cancer trials
    (841, "general", "[PMC5803577] According to PMC5803577, what proportion of registered breast cancer trials listed in ClinicalTrials.gov had been published?"),
    (842, "general", "[PMC5803577] According to PMC5803577, what was the median time to publication for registered breast cancer trials?"),
    (843, "general", "[PMC5803577] According to PMC5803577, how many breast cancer trials were published within 24 months of completion?"),
    (844, "general", "[PMC5803577] According to PMC5803577, was there a significant increase in publication proportions of breast cancer trials after the introduction of the ClinicalTrials.gov results database?"),
    (845, "general", "[PMC5803577] According to PMC5803577, what trial characteristics were associated with publication of registered breast cancer trials?"),

    # PMC2206501 - Pediatrics: Cardiovascular topics in PICU 2006
    (846, "general", "[PMC2206501] According to PMC2206501, what cardiovascular topics in paediatric intensive care were summarized from papers published in 2006?"),
    (847, "general", "[PMC2206501] According to PMC2206501, what was the role of arginine-vasopressin and terlipressin in catecholamine-resistant septic shock in children?"),
    (848, "general", "[PMC2206501] According to PMC2206501, what were the findings regarding AVP infusion in extremely low birth weight infants with catecholamine-resistant shock?"),

    # PMC12232468 - Pulmonology: COPD standardized management trial
    (849, "general", "[PMC12232468] According to PMC12232468, how many secondary hospitals are involved in the nationwide COPD standardized management trial in China?"),
    (850, "general", "[PMC12232468] According to PMC12232468, what are the five components of the integrated intervention in the standardized management group of the COPD trial?"),

    # ===== EMERGENCY QUESTIONS (851-900) =====
    # PMC1236923 - Cardiology
    (851, "emergency", "[PMC1236923] Based on PMC1236923, a primary care physician in a country with no national heart failure guideline asks which guideline to follow — what does the study show about guideline use in such countries?"),
    (852, "emergency", "[PMC1236923] Based on PMC1236923, a cardiologist notes low beta-blocker prescribing in their country — what range of beta-blocker use did the IMPROVEMENT-HF study find across European primary care settings?"),
    (853, "emergency", "[PMC1236923] Based on PMC1236923, a health system wants to improve heart failure prescribing by aligning with guidelines — what does the study conclude about the relationship between guideline recommendations and actual prescribing?"),

    # PMC11846407 - Emergency: Sepsis guidelines quality
    (854, "emergency", "[PMC11846407] Based on PMC11846407, a clinician is selecting a sepsis management guideline for their ICU — which quality threshold distinguishes high-quality guidelines in this AGREE II assessment?"),
    (855, "emergency", "[PMC11846407] Based on PMC11846407, an emergency physician notes that sepsis guideline recommendations are mostly weak — what percentage of recommendations in the reviewed guidelines were classified as weak strength?"),
    (856, "emergency", "[PMC11846407] Based on PMC11846407, a hospital quality team wants to improve sepsis guideline applicability — which AGREE II domain had the lowest average score and what was it?"),
    (857, "emergency", "[PMC11846407] Based on PMC11846407, a researcher is evaluating the evidence base for sepsis guidelines — what was the predominant level of evidence cited in the reviewed sepsis infection management guidelines?"),

    # PMC2898118 - Endocrinology
    (858, "emergency", "[PMC2898118] Based on PMC2898118, a primary care clinic is implementing a diabetes care manager program — what percentage of patients expressed willingness to work with a care manager for diabetes management?"),
    (859, "emergency", "[PMC2898118] Based on PMC2898118, a provider wants to expand care manager services to other chronic diseases — what does the study show about patient willingness to see a care manager for non-diabetes chronic problems?"),
    (860, "emergency", "[PMC2898118] Based on PMC2898118, a care team is identifying patients less likely to engage with a care manager — what patient factor was associated with decreased likelihood to work with a care manager?"),

    # PMC12400259 - Gastroenterology
    (861, "emergency", "[PMC12400259] Based on PMC12400259, an IBD patient is malnourished and asks about dietary support — what does the paper identify as the main barrier patients face in accessing specialist nutrition advice?"),
    (862, "emergency", "[PMC12400259] Based on PMC12400259, a gastroenterology unit is building a multidisciplinary IBD team — what evidence does the paper provide for including a dietitian in the IBD MDT?"),
    (863, "emergency", "[PMC12400259] Based on PMC12400259, a hospital administrator questions whether dietitians are necessary in IBD care — what does the paper state about IBD MDTs that include dietitians versus those that do not?"),
    (864, "emergency", "[PMC12400259] Based on PMC12400259, a dietitian is asked to justify their role in IBD management — what unique qualifications make dietitians the most appropriate professional for nutritional assessment in IBD?"),

    # PMC11638529 - Infectious disease
    (865, "emergency", "[PMC11638529] Based on PMC11638529, a nursing school is reviewing its antimicrobial stewardship curriculum — what specific knowledge gaps were identified in UK pre-registration nursing students?"),
    (866, "emergency", "[PMC11638529] Based on PMC11638529, a nurse educator wants to improve antimicrobial stewardship training — what modes of education delivery did student nurses prefer for antimicrobial stewardship?"),
    (867, "emergency", "[PMC11638529] Based on PMC11638529, a hospital is considering interprofessional antimicrobial stewardship education — what benefits did students report from shared teaching with other professions?"),
    (868, "emergency", "[PMC11638529] Based on PMC11638529, a nursing program director wants to strengthen antimicrobial stewardship competencies — in which competency areas did students feel least prepared?"),

    # PMC3701497 - Nephrology
    (869, "emergency", "[PMC3701497] Based on PMC3701497, a CKD stage 3 patient with diabetes and albuminuria presents with uncontrolled hypertension — what does the study show about BP control rates in this high-risk subgroup?"),
    (870, "emergency", "[PMC3701497] Based on PMC3701497, a nephrologist reviews a CKD stage 3 patient on only one antihypertensive — what proportion of CKD stage 3 patients with hypertension were on monotherapy in this study?"),
    (871, "emergency", "[PMC3701497] Based on PMC3701497, a primary care physician is managing an elderly CKD stage 3 patient with hypertension — how does age affect the likelihood of achieving systolic versus diastolic BP targets?"),
    (872, "emergency", "[PMC3701497] Based on PMC3701497, a quality improvement team wants to set BP targets for CKD stage 3 patients — what three BP control standards were used to assess BP control in this study?"),
    (873, "emergency", "[PMC3701497] Based on PMC3701497, a primary care practice wants to improve BP control in CKD patients — what does the study suggest about using more antihypertensive agents in combination?"),

    # PMC10640530 - Neurology
    (874, "emergency", "[PMC10640530] Based on PMC10640530, an acute ischemic stroke patient is ineligible for endovascular therapy — what adjunctive CBF-enhancing therapies does the review identify as most promising?"),
    (875, "emergency", "[PMC10640530] Based on PMC10640530, a neurologist is considering Fasudil for a stroke patient — what is the mechanism by which Fasudil may enhance cerebral blood flow in acute ischemic stroke?"),
    (876, "emergency", "[PMC10640530] Based on PMC10640530, a stroke team is evaluating remote ischemic perconditioning — what does PMC10640530 identify as the potential benefit of this intervention in acute ischemic stroke?"),
    (877, "emergency", "[PMC10640530] Based on PMC10640530, a stroke researcher is studying collateral circulation — what does the review state about the role of pial collaterals and genetics in acute ischemic stroke outcomes?"),
    (878, "emergency", "[PMC10640530] Based on PMC10640530, a clinician asks about Sanguinate for stroke — what type of agent is Sanguinate and what is its proposed mechanism for enhancing CBF in acute ischemic stroke?"),

    # PMC4451740 - Obstetrics
    (879, "emergency", "[PMC4451740] Based on PMC4451740, a patient presents with severe pre-eclampsia at a Nigerian health facility — what percentage of facilities had magnesium sulphate available and what were the main supply barriers?"),
    (880, "emergency", "[PMC4451740] Based on PMC4451740, a health facility manager in Northern Nigeria wants to improve eclampsia management — what integrated program components does the study recommend?"),
    (881, "emergency", "[PMC4451740] Based on PMC4451740, a provider at a Nigerian facility has not been trained on MgSO4 — what percentage of providers in the study had received training on MgSO4 for PE/E management?"),
    (882, "emergency", "[PMC4451740] Based on PMC4451740, an obstetric emergency team is assessing facility readiness for pre-eclampsia management — what essential equipment and supply gaps were identified in Northern Nigerian facilities?"),
    (883, "emergency", "[PMC4451740] Based on PMC4451740, a maternal health program is designing interventions to improve MgSO4 use — what were the key facilitators identified for magnesium sulphate use in pre-eclampsia management?"),

    # PMC5803577 - Oncology
    (884, "emergency", "[PMC5803577] Based on PMC5803577, an oncology researcher is assessing publication bias in breast cancer trials — what proportion of registered trials remained unpublished?"),
    (885, "emergency", "[PMC5803577] Based on PMC5803577, a clinical trial investigator wants to understand publication timelines — what was the median time to publication for registered breast cancer trials and what proportion were published within 24 months?"),
    (886, "emergency", "[PMC5803577] Based on PMC5803577, a systematic reviewer is assessing whether the ClinicalTrials.gov results database improved publication rates — what did the study find about publication proportions before versus after the database introduction?"),
    (887, "emergency", "[PMC5803577] Based on PMC5803577, a researcher is identifying factors that predict trial publication — what trial characteristics were independently associated with publication of registered breast cancer trials?"),

    # PMC2206501 - Pediatrics
    (888, "emergency", "[PMC2206501] Based on PMC2206501, a child presents with catecholamine-resistant septic shock — what rescue therapies were studied in paediatric ICU patients with this condition according to the 2006 review?"),
    (889, "emergency", "[PMC2206501] Based on PMC2206501, an extremely low birth weight infant develops catecholamine-resistant septic shock — what did the study by Meyer et al. report about AVP infusion outcomes in this population?"),
    (890, "emergency", "[PMC2206501] Based on PMC2206501, a PICU team is considering terlipressin for a child with refractory septic shock — what was the study design and findings of the Rodriguez-Nunez terlipressin trial in children?"),

    # PMC12232468 - Pulmonology
    (891, "emergency", "[PMC12232468] Based on PMC12232468, a COPD patient in GOLD Group B is being enrolled in a standardized management program — what five intervention components will they receive?"),
    (892, "emergency", "[PMC12232468] Based on PMC12232468, a pulmonologist wants to know the target population for the COPD STANDARD trial — which GOLD 2023 ABE classification groups are eligible for enrollment?"),
    (893, "emergency", "[PMC12232468] Based on PMC12232468, a hospital is deciding whether to implement standardized COPD management — what is the primary goal of the COPD STANDARD trial and when is it expected to complete?"),

    # PMC4775830 - Radiology
    (894, "general", "[PMC4775830] According to PMC4775830, what was the overarching theme identified in the study of radiographer-referrer communication in rural Australian practice?"),
    (895, "general", "[PMC4775830] According to PMC4775830, what indirect communication strategies did rural radiographers use when direct communication pathways were blocked?"),
    (896, "general", "[PMC4775830] According to PMC4775830, what factors enabled direct communication pathways between rural radiographers and referring doctors?"),
    (897, "general", "[PMC4775830] According to PMC4775830, what barriers shaped by historical hierarchical relationships limited direct communication between radiographers and referrers?"),
    (898, "emergency", "[PMC4775830] Based on PMC4775830, a rural radiographer identifies an abnormality but the referring doctor appears to have missed it — what strategies does the study describe for radiographers in this situation?"),
    (899, "emergency", "[PMC4775830] Based on PMC4775830, a rural health service wants to improve radiographer-referrer communication — what does the study recommend for strengthening interprofessional communication pathways?"),
    (900, "emergency", "[PMC4775830] Based on PMC4775830, a radiographer in rural practice lacks confidence in communicating radiographic findings — what does the study identify as the root causes of this communication barrier?"),
]

# Write to CSV
import csv

with open("docs/test_questions_800.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for q_id, q_type, q_text in questions:
        writer.writerow([q_id, q_type, q_text])

print(f"Added {len(questions)} questions (IDs 801-900)")
print("Done!")
