"""
Health & Fluctuation Engine for Relax
Calculates endocrine impacts, period fluctuation margins, cycle shifts,
predictability scores, and personalized clinical guidance for conditions like
thyroid disorders, PCOS, endometriosis, and chronic stress.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Any

# Clinical knowledge base for thyroid and reproductive health factors
HEALTH_CONDITIONS_CATALOG = {
    "thyroid": {
        "None / Normal Thyroid": {
            "name": "Normal Thyroid",
            "cycle_shift": 0,
            "period_shift": 0,
            "variance": 1,
            "penalty": 0,
            "mechanism": "Thyroid hormones (T3/T4) and TSH are within reference ranges, maintaining balanced HPO (hypothalamic-pituitary-ovarian) axis signaling.",
            "care_tip": "Maintain baseline thyroid wellness with balanced dietary iodine and selenium.",
            "phase_tips": {}
        },
        "Hypothyroidism (Underactive)": {
            "name": "Hypothyroidism (Underactive)",
            "cycle_shift": 3,
            "period_shift": 1,
            "variance": 5,
            "penalty": 22,
            "mechanism": "Low T3/T4 levels trigger compensatory elevated TRH and TSH from the pituitary. High TRH stimulates prolactin secretion (hyperprolactinemia), which directly inhibits pulsatile GnRH secretion. This delays follicular development, postpones ovulation, extends cycle length, and causes heavier, prolonged bleeding.",
            "care_tip": "Support thyroid metabolism: consume selenium (1-2 Brazil nuts daily), zinc, and adequate protein. Avoid excessive raw cruciferous vegetables around ovulation. Keep warm with warming spices like ginger and cinnamon.",
            "phase_tips": {
                "menstrual": "🩸 Hypothyroid Advisory: Menorrhagia (heavy flow) and severe fatigue are common due to lower basal metabolic rate and clotting factor shifts. Rest with heat and replenish iron.",
                "follicular": "🌿 Hypothyroid Advisory: Follicular growth may be slower. Gentle strength workouts support metabolic health without overstressing adrenals.",
                "ovulation": "🟣 Hypothyroid Advisory: Ovulation may be delayed by 3–6 days compared to typical calendar models. Monitor basal body temperature.",
                "luteal": "🌼 Hypothyroid Advisory: Progesterone drops can exacerbate low core temperature, cold extremities, and sluggish digestion.",
                "pms": "✨ Hypothyroid Advisory: Pre-menstrual sluggishness, water retention, and depressive mood dips may feel heightened."
            }
        },
        "Hyperthyroidism (Overactive)": {
            "name": "Hyperthyroidism (Overactive)",
            "cycle_shift": -2,
            "period_shift": -1,
            "variance": 4,
            "penalty": 20,
            "mechanism": "Excess circulating thyroid hormones stimulate hepatic production of sex hormone-binding globulin (SHBG) and accelerate estrogen clearance. This lowers bioactive free estradiol, leading to shorter cycle lengths, hypomenorrhea (scanty bleeding), or sporadic anovulatory cycles.",
            "care_tip": "Support the nervous system: limit high-dose caffeine and stimulants. Ensure adequate caloric density and magnesium to protect against accelerated resting metabolic rate.",
            "phase_tips": {
                "menstrual": "🩸 Hyperthyroid Advisory: Flow is often lighter and shorter in duration. Monitor resting heart rate and stay well-hydrated.",
                "follicular": "🌿 Hyperthyroid Advisory: Rapid estrogen peaks can trigger irritability or anxiety. Incorporate grounding, parasympathetic practices.",
                "ovulation": "🟣 Hyperthyroid Advisory: Ovulation may occur earlier than Day 14 or intermittently skip. Avoid overheating.",
                "luteal": "🌼 Hyperthyroid Advisory: High metabolic heat production can worsen sleep disruption during the warm luteal phase.",
                "pms": "✨ Hyperthyroid Advisory: Pre-menstrual palpitations, heat sensitivity, and heightened nervousness require cooling foods and restful routines."
            }
        },
        "Hashimoto's Thyroiditis": {
            "name": "Hashimoto's Thyroiditis",
            "cycle_shift": 3,
            "period_shift": 1,
            "variance": 6,
            "penalty": 24,
            "mechanism": "Autoimmune lymphocytic infiltration causes cyclical thyroid tissue damage. Variable antibody flare-ups create fluctuating thyroid hormone levels, leading to unpredictable ovulation delays and fluctuating cycle lengths.",
            "care_tip": "Prioritize gut barrier integrity and anti-inflammatory nutrition: incorporate omega-3 fatty acids, turmeric, bone broth, and manage autoimmune triggers.",
            "phase_tips": {
                "menstrual": "🩸 Hashimoto's Advisory: Immune flares can accompany period onset. Prioritize anti-inflammatory rest and warm herbal teas.",
                "ovulation": "🟣 Hashimoto's Advisory: Ovulatory timing fluctuates based on autoimmune antibody activity. Expect variable fertile windows.",
                "pms": "✨ Hashimoto's Advisory: Heightened brain fog and joint tenderness may manifest 4-7 days prior to bleeding."
            }
        }
    },
    "conditions": {
        "PCOS / PCOD": {
            "name": "PCOS / PCOD",
            "cycle_shift": 6,
            "period_shift": 0,
            "variance": 8,
            "penalty": 28,
            "mechanism": "Elevated luteinizing hormone (LH) and localized ovarian hyperandrogenism disrupt follicle selection, preventing dominant follicle maturation. This causes substantial ovulatory delay, prolonged follicular phases (often 32–45+ days), and irregular cycle intervals.",
            "care_tip": "Focus on insulin sensitivity: pair carbohydrates with dietary fiber and healthy fats, consider myo-inositol, and enjoy spearmint tea for gentle androgen support.",
            "phase_tips": {
                "follicular": "🌿 PCOS Advisory: Follicular phase is often prolonged. Cervical fluid may show multiple false fertile peaks before true ovulation.",
                "ovulation": "🟣 PCOS Advisory: Ovulation is delayed or sporadic. Ovulation predictor kits (OPKs) may show false positives due to baseline high LH.",
                "pms": "✨ PCOS Advisory: Extended estrogen dominance without sufficient progesterone can heighten cravings and cystic acne."
            }
        },
        "Endometriosis": {
            "name": "Endometriosis",
            "cycle_shift": 0,
            "period_shift": 2,
            "variance": 3,
            "penalty": 15,
            "mechanism": "Ectopic endometrial tissue produces prostaglandins and inflammatory cytokines, inducing localized progesterone resistance and extensive pelvic muscle contraction. Bleeding is often prolonged and accompanied by severe dysmenorrhea.",
            "care_tip": "Manage inflammation: emphasize curcumin, ginger, magnesium glycinate, and topical castor oil packs or heat therapy (avoiding abdomen during active bleeding).",
            "phase_tips": {
                "menstrual": "🩸 Endo Advisory: High prostaglandin release triggers intense cramping and possible bowel/pelvic pain. Apply warm heat early.",
                "ovulation": "🟣 Endo Advisory: Peritoneal inflammation can cause localized mid-cycle pelvic twinges (mittelschmerz).",
                "pms": "✨ Endo Advisory: Pelvic inflammation begins rising 3–5 days prior to bleeding onset. Gentle restorative stretching is beneficial."
            }
        },
        "Uterine Fibroids": {
            "name": "Uterine Fibroids",
            "cycle_shift": 0,
            "period_shift": 2,
            "variance": 3,
            "penalty": 12,
            "mechanism": "Benign myometrial tumors expand the vascular surface area of the uterine cavity and compromise muscular contraction, leading to heavy menstrual bleeding (menorrhagia) and extended duration.",
            "care_tip": "Replenish ferritin: combine non-heme iron sources (spinach, lentils) with vitamin C for maximum absorption.",
            "phase_tips": {
                "menstrual": "🩸 Fibroids Advisory: Heavy flow requires close iron and hydration replenishment. Avoid intense abdominal straining."
            }
        },
        "Perimenopause": {
            "name": "Perimenopause",
            "cycle_shift": 4,
            "period_shift": -1,
            "variance": 7,
            "penalty": 25,
            "mechanism": "Declining ovarian follicular reserves lead to erratic fluctuations in estradiol and inhibin-B. Cycles may alternate between abnormally short and widely spaced intervals.",
            "care_tip": "Support hormone clearance and adrenal health: prioritize resistance training, calcium, vitamin D3, and adequate protein.",
            "phase_tips": {
                "luteal": "🌼 Perimenopause Advisory: Progesterone drops steeply, occasionally causing night sweats and sleep fragmentation.",
                "pms": "✨ Perimenopause Advisory: Emotional volatility and vasomotor symptoms (hot flashes) can intensify pre-menstrually."
            }
        },
        "Hormonal Birth Control": {
            "name": "Hormonal Birth Control",
            "cycle_shift": 0,
            "period_shift": -1,
            "variance": 1,
            "penalty": 5,
            "mechanism": "Exogenous synthetic progestins and estrogens suppress the endogenous pituitary LH surge. Bleeding is a scheduled withdrawal bleed rather than physiological menstruation.",
            "care_tip": "Synthetic hormones can deplete micronutrients; ensure adequate B-complex vitamins, magnesium, and zinc.",
            "phase_tips": {
                "menstrual": "🩸 Birth Control Note: Bleeding represents withdrawal from active hormone pills rather than true post-ovulatory menses."
            }
        }
    },
    "stress": {
        "Low / Managed": {
            "name": "Low Stress",
            "cycle_shift": 0,
            "variance": 0,
            "penalty": 0,
            "mechanism": "HPA axis is calm; cortisol rhythm does not interfere with hypothalamic GnRH release.",
            "care_tip": "Continue your healthy stress-management habits.",
            "phase_tips": {}
        },
        "Moderate": {
            "name": "Moderate Stress",
            "cycle_shift": 1,
            "variance": 2,
            "penalty": 8,
            "mechanism": "Mild transient cortisol elevation can occasionally delay the pre-ovulatory LH surge by 1 to 2 days.",
            "care_tip": "Incorporate 10 minutes of daily mindfulness or breathwork to prevent cortisol accumulation.",
            "phase_tips": {
                "follicular": "🌿 Stress Note: Moderate stress can delay the LH surge by 1-2 days.",
                "pms": "✨ Stress Note: Cortisol competes with progesterone receptors, which can amplify PMS mood shifts."
            }
        },
        "High / Chronic Stress / Burnout": {
            "name": "High / Chronic Stress",
            "cycle_shift": 3,
            "variance": 4,
            "penalty": 18,
            "mechanism": "Sustained high cortisol stimulates corticotropin-releasing hormone (CRH), which directly suppresses pituitary GnRH pulsatility. This can stall follicular maturation, delay ovulation by several days, or trigger functional cycle delays.",
            "care_tip": "Prioritize nervous system recovery: practice 4-7-8 breathing, take magnesium glycinate before bed, avoid intense fasting or extreme HIIT workouts, and protect 8 hours of sleep.",
            "phase_tips": {
                "follicular": "🌿 High Stress Alert: Elevated cortisol can inhibit GnRH, pushing ovulation back by 3–5 days.",
                "ovulation": "🟣 High Stress Alert: Chronic stress may cause anovulatory cycles or delayed fertile windows.",
                "luteal": "🌼 High Stress Alert: High cortisol accelerates progesterone depletion, shortening luteal phases.",
                "pms": "✨ High Stress Alert: Pre-menstrual anxiety, insomnia, and irritability are significantly heightened."
            }
        }
    }
}

def calculate_health_fluctuations(
    thyroid_status: str,
    health_conditions: List[str],
    stress_level: str,
    base_cycle_length: int = 28,
    base_period_length: int = 5
) -> Dict[str, Any]:
    """
    Computes clinical cycle fluctuations, variance margin (± days),
    estimated cycle length adjustments, predictability score, and personalized guidance.
    """
    # Clean input keys
    t_key = thyroid_status if thyroid_status in HEALTH_CONDITIONS_CATALOG["thyroid"] else "None / Normal Thyroid"
    s_key = stress_level if stress_level in HEALTH_CONDITIONS_CATALOG["stress"] else "Low / Managed"
    if s_key == "Normal":
        s_key = "Low / Managed"

    t_data = HEALTH_CONDITIONS_CATALOG["thyroid"].get(t_key, HEALTH_CONDITIONS_CATALOG["thyroid"]["None / Normal Thyroid"])
    s_data = HEALTH_CONDITIONS_CATALOG["stress"].get(s_key, HEALTH_CONDITIONS_CATALOG["stress"]["Low / Managed"])

    cycle_shift = t_data["cycle_shift"] + s_data["cycle_shift"]
    period_shift = t_data["period_shift"]
    variance_sum = t_data["variance"] + s_data["variance"]
    penalty_sum = t_data["penalty"] + s_data["penalty"]

    active_condition_data = []
    for cond in health_conditions:
        # Match condition
        for cat_key, cat_val in HEALTH_CONDITIONS_CATALOG["conditions"].items():
            if cond == cat_key or cond in cat_key or cat_key in cond:
                active_condition_data.append(cat_val)
                cycle_shift += cat_val["cycle_shift"]
                period_shift += cat_val["period_shift"]
                variance_sum += cat_val["variance"]
                penalty_sum += cat_val["penalty"]
                break

    # Calculate final fluctuation margin (± days)
    # Baseline physiological variance is 1-2 days. Max realistic biological cap is 14 days.
    fluctuation_margin = min(14, max(1, round(variance_sum)))

    # Adjust expected cycle length
    adjusted_cycle_length = max(21, min(45, base_cycle_length + cycle_shift))
    adjusted_period_length = max(2, min(10, base_period_length + period_shift))

    # Calculate Predictability Score (0 - 100%)
    raw_score = 96 - penalty_sum
    predictability_score = max(42, min(98, raw_score))

    if predictability_score >= 85:
        predictability_rating = "High Predictability 🟢"
        predictability_desc = "Cycles follow a regular rhythm with minimal expected deviation (±1 to ±2 days)."
        badge_class = "badge-fertile"
    elif predictability_score >= 68:
        predictability_rating = "Moderate Fluctuation 🟡"
        predictability_desc = f"Hormonal factors introduce a fluctuation window of ±{fluctuation_margin} days."
        badge_class = "badge-countdown"
    else:
        predictability_rating = "High Fluctuation 🟠"
        predictability_desc = f"Significant hormonal variance detected. Cycle timing may fluctuate by ±{fluctuation_margin} days."
        badge_class = "badge-phase"

    # Assemble Clinical Explanations
    insights = []
    care_tips = []
    phase_advisories = {}

    if t_key != "None / Normal Thyroid":
        insights.append({
            "title": f"Thyroid Influence ({t_data['name']})",
            "mechanism": t_data["mechanism"],
            "impact": f"Tends to shift cycle length by {t_data['cycle_shift']:+d} days and adds ±{t_data['variance']} days fluctuation."
        })
        care_tips.append(t_data["care_tip"])
        for phase, tip in t_data.get("phase_tips", {}).items():
            phase_advisories.setdefault(phase, []).append(tip)

    for c_data in active_condition_data:
        insights.append({
            "title": f"Condition: {c_data['name']}",
            "mechanism": c_data["mechanism"],
            "impact": f"Shifts cycle length by {c_data['cycle_shift']:+d} days and adds ±{c_data['variance']} days fluctuation."
        })
        care_tips.append(c_data["care_tip"])
        for phase, tip in c_data.get("phase_tips", {}).items():
            phase_advisories.setdefault(phase, []).append(tip)

    if s_key in ["Moderate", "High / Chronic Stress / Burnout"]:
        insights.append({
            "title": f"Stress Influence ({s_data['name']})",
            "mechanism": s_data["mechanism"],
            "impact": f"Elevated cortisol can delay ovulation by {s_data['cycle_shift']:+d} days with ±{s_data['variance']} days variance."
        })
        care_tips.append(s_data["care_tip"])
        for phase, tip in s_data.get("phase_tips", {}).items():
            phase_advisories.setdefault(phase, []).append(tip)

    if not insights:
        insights.append({
            "title": "Regular Hormonal Balance",
            "mechanism": "No disruptive thyroid, chronic stress, or gynecological conditions reported.",
            "impact": "Cycles are expected to occur within the standard ±1 to ±2 day physiological margin."
        })
        care_tips.append("Maintain consistent sleep, whole-food nutrition, and moderate daily movement.")

    factors = []
    if t_key != "None / Normal Thyroid":
        factors.append(t_key)
    for c in active_condition_data:
        factors.append(c["name"])
    if s_key not in ["Low / Managed", "Normal"]:
        factors.append(f"Stress: {s_key}")

    # Return comprehensive analysis
    return {
        "fluctuation_margin": fluctuation_margin,
        "base_cycle_length": base_cycle_length,
        "adjusted_cycle_length": adjusted_cycle_length,
        "cycle_shift": cycle_shift,
        "base_period_length": base_period_length,
        "adjusted_period_length": adjusted_period_length,
        "period_shift": period_shift,
        "predictability_score": predictability_score,
        "predictability_rating": predictability_rating,
        "predictability_desc": predictability_desc,
        "badge_class": badge_class,
        "insights": insights,
        "care_tips": care_tips,
        "phase_advisories": phase_advisories,
        "active_factors_summary": factors
    }

def get_fluctuation_window(target_date: date, margin_days: int) -> Tuple[date, date, str]:
    """Returns the earliest expected date, latest expected date, and formatted string."""
    earliest = target_date - timedelta(days=margin_days)
    latest = target_date + timedelta(days=margin_days)
    formatted = f"{earliest.strftime('%d %b')} – {latest.strftime('%d %b %Y')} (±{margin_days}d)"
    return earliest, latest, formatted

# ---------------------------------------------------------
# Cycle-Synced Diet & Nutrition Engine
# ---------------------------------------------------------
CYCLE_DIET_PROTOCOLS = {
    "menstrual": {
        "key": "menstrual",
        "name": "Menstrual Phase (Period) 🩸",
        "tagline": "Iron Replenishment, Muscle Relaxation & Anti-Cramping Comfort",
        "biology": "Estradiol and progesterone are at baseline. The endometrium sheds under the influence of localized prostaglandins, causing uterine contractions. Nourishment should focus on restoring iron reserves, lowering inflammatory prostaglandins, and warming, easy digestion.",
        "key_nutrients": ["Heme & Non-Heme Iron + Vitamin C", "Magnesium Glycinate", "Omega-3 Fatty Acids", "Electrolytes & Warm Fluids"],
        "superfoods": [
            ("🥩 Iron & Blood Replenishers", "Lentils, baby spinach, grass-fed beef, black beans, pumpkin seeds — pair with Vitamin C (citrus, bell peppers) to maximize iron bioavailability."),
            ("🍵 Anti-Cramping Botanicals", "Warm ginger tea (naturally inhibits inflammatory COX-2 and prostaglandin synthesis), chamomile, and soothing bone/miso broths."),
            ("🍫 Magnesium Smooth-Muscle Calmers", "70%+ dark chocolate, pumpkin seeds, almonds, and avocados to ease uterine muscle spasms and diminish headache tension."),
            ("🥑 Healthy Anti-Inflammatory Lipids", "Walnuts, chia seeds, extra virgin olive oil, and wild salmon to decrease inflammatory pain signals.")
        ],
        "foods_to_avoid": [
            "Excessive caffeine (vasoconstricts uterine blood supply, intensifying cramping)",
            "Excess sodium & processed snacks (amplifies fluid retention, bloating, and breast tenderness)",
            "Ice-cold beverages and raw foods (can trigger gastrointestinal spasms and sluggish digestion)"
        ],
        "sample_meals": {
            "Breakfast": "Warm steel-cut oatmeal with sliced banana, toasted pumpkin seeds, cinnamon, and a square of dark chocolate.",
            "Lunch": "Hearty iron-rich lentil soup with wilted baby spinach and fresh lemon squeeze.",
            "Dinner": "Wild salmon or savory tempeh with roasted sweet potatoes and garlic-sautéed broccoli.",
            "Bedtime Care": "Steaming cup of fresh ginger or chamomile tea with a touch of raw honey."
        }
    },
    "follicular": {
        "key": "follicular",
        "name": "Follicular & High Fertility Window 🌱",
        "tagline": "Cellular Vitality, Follicular Maturation & Estrogen Detoxification",
        "biology": "Pituitary FSH stimulates ovarian follicle development while rising estradiol thickens the uterine lining and produces receptive, fertile cervical fluid. Insulin sensitivity and metabolic efficiency are at their highest.",
        "key_nutrients": ["Folate & Methylation Catalysts", "Cruciferous Indoles (DIM)", "Probiotic Cultures", "Seed Cycling (Phase 1)"],
        "superfoods": [
            ("🥦 Estrogen Clearance & Liver Support", "Cruciferous vegetables (broccoli sprouts, cauliflower, Brussels sprouts, kale) rich in DIM and Sulforaphane to aid hepatic estrogen metabolism."),
            ("🥗 Probiotic Estrobolome Nourishment", "Fermented foods (kimchi, sauerkraut, organic kefir, live-culture yogurt) to nurture gut bacteria that ensure healthy estrogen elimination."),
            ("🌰 Follicular Seed Cycling", "1 tbsp each of freshly ground raw flaxseeds and pumpkin seeds daily (supplies protective lignans and zinc for oocyte quality)."),
            ("🥑 Oocyte Quality & Conception Lipids", "Pastured eggs (rich in choline for cellular integrity), avocado, sprouted chickpeas, and extra virgin olive oil.")
        ],
        "foods_to_avoid": [
            "Industrial trans fats & heavy fried foods (exert oxidative stress on maturing ovarian follicles)",
            "Excess alcohol (interferes with hepatic clearance of rising estradiol)"
        ],
        "sample_meals": {
            "Breakfast": "Vibrant green smoothie with probiotic kefir or plant milk, baby kale, ground flaxseed, and blueberries.",
            "Lunch": "Mediterranean salad bowl with mixed greens, boiled pastured egg, chickpeas, sliced avocado, and olive oil vinaigrette.",
            "Dinner": "Herb-roasted pasture-raised chicken or tofu with quinoa, snap peas, and steamed broccoli sprouts.",
            "Snack / Treat": "Crisp green apple slices with raw almond butter and pumpkin seeds."
        }
    },
    "ovulation": {
        "key": "ovulation",
        "name": "Ovulation Peak Day 🟣",
        "tagline": "Egg Cellular Protection, Peak Hydration & Vascular Microcirculation",
        "biology": "Peak estradiol triggers the pre-ovulatory LH surge, releasing the dominant oocyte. Basal energy, libido, and cervical mucus fluid production are at their absolute cycle peak.",
        "key_nutrients": ["Potent Polyphenols & Glutathione", "Omega-3 Fatty Acids", "Zinc & L-Arginine", "Deep Cellular Hydration"],
        "superfoods": [
            ("🍓 Oocyte Shield Antioxidants", "Deep-colored berries (blueberries, blackberries), pomegranate seeds, and heirloom tomatoes (glutathione & lycopene to shield the egg from oxidative stress)."),
            ("💧 Cervical Mucus Hydrators", "Raw coconut water, cucumber, celery, and citrus-infused water for optimal thin, alkaline egg-white cervical fluid."),
            ("🐟 Ovarian Vascularity Lipids", "Wild Alaskan salmon, sardines, chia seeds, and walnuts to support pelvic microcirculation."),
            ("🌾 Folate & Zinc Powerhouses", "Steamed asparagus, sesame seeds, lentils, and dark leafy greens.")
        ],
        "foods_to_avoid": [
            "Refined sweets & high-glycemic carbohydrates (trigger abrupt insulin surges that can disturb LH surge harmony)",
            "Dehydrating sodas and high caffeine without abundant water"
        ],
        "sample_meals": {
            "Breakfast": "Coconut chia seed pudding topped with fresh blackberries, raspberries, and pomegranate arils.",
            "Lunch": "Citrus-quinoa bowl with steamed asparagus, avocado, pumpkin seeds, and grilled salmon or edamame.",
            "Dinner": "Pan-seared cod or herb-baked tempeh with roasted zucchini, bell peppers, and fresh parsley.",
            "Hydration Booster": "Chilled coconut water infused with fresh mint and lime."
        }
    },
    "luteal": {
        "key": "luteal",
        "name": "Luteal Phase & Pre-Menstrual Window (PMS) ✨",
        "tagline": "Progesterone Synthesis, Serotonin Sustainment & De-Bloating Botanicals",
        "biology": "The corpus luteum secretes progesterone to maintain the secretory endometrium. Basal metabolic rate increases by ~100–300 kcal/day while brain serotonin levels drop. Aldosterone can promote water and salt retention.",
        "key_nutrients": ["Vitamin B6 & Magnesium", "Slow Complex Carbohydrates", "Potassium & Electrolytes", "Luteal Seed Cycling (Phase 2)"],
        "superfoods": [
            ("🍠 Serotonin & Metabolism Carbs", "Roasted sweet potatoes, butternut squash, oats, and quinoa to elevate central serotonin naturally, prevent mood crashes, and fuel higher metabolic burn."),
            ("🌻 Luteal Seed Cycling", "1 tbsp each of raw sunflower seeds and sesame seeds daily (supplies zinc, selenium, and Vitamin E to sustain healthy progesterone levels)."),
            ("🥒 De-Bloating Botanicals", "Cucumber, celery, dandelion root tea, and peppermint tea to assist kidney fluid filtration and diminish abdominal distension."),
            ("🍌 Vitamin B6 & Neurotransmitter Support", "Bananas, chickpeas, walnuts, pasture-raised poultry, and dark leafy greens to ease breast tenderness and pre-menstrual mood dips.")
        ],
        "foods_to_avoid": [
            "Refined sugars & candy (induces steep blood glucose crashes that exacerbate irritability and fatigue)",
            "High sodium & packaged snacks (massively amplifies pre-menstrual water retention and breast tenderness)",
            "Alcohol (disrupts luteal sleep architecture and lowers mood resilience)"
        ],
        "sample_meals": {
            "Breakfast": "Warm cinnamon-spiced oats with banana slices, raw sunflower seeds, walnuts, and a splash of oat milk.",
            "Lunch": "Roasted butternut squash and black bean salad with sesame dressing and pumpkin seeds.",
            "Dinner": "Turkey or lentil chili served over roasted sweet potato wedges with steamed greens.",
            "Evening Ritual": "Warm dandelion root or peppermint tea to support digestion and ease bloat."
        }
    }
}

def get_diet_suggestions(phase_name: str, health_factors: list = None) -> dict:
    """Returns curated diet and nutrition suggestions tailored to the active cycle phase."""
    p_lower = phase_name.lower()
    if "menstrual" in p_lower or "period" in p_lower or "bleed" in p_lower:
        base = dict(CYCLE_DIET_PROTOCOLS["menstrual"])
    elif "ovulation" in p_lower:
        base = dict(CYCLE_DIET_PROTOCOLS["ovulation"])
    elif "fertile" in p_lower or "follicular" in p_lower:
        base = dict(CYCLE_DIET_PROTOCOLS["follicular"])
    else:
        base = dict(CYCLE_DIET_PROTOCOLS["luteal"])
        
    return base

def get_all_cycle_diet_guides() -> dict:
    """Returns all 4 comprehensive phase diet protocols for full cycle browsing."""
    return CYCLE_DIET_PROTOCOLS
