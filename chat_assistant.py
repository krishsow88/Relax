"""
Relax Chat Assistant Module
Provides intelligent, cycle-aware, empathetic, and scientifically grounded responses
for the Relax Menstrual Wellness AI Chat interface.
"""

from datetime import date
from typing import Dict, Any, List

def generate_chat_reply(prompt: str, ctx: Dict[str, Any]) -> str:
    """
    Generate an empathetic, context-aware reply to user queries.
    Uses user's active cycle phase, cycle day, health conditions, countdown,
    and clinical knowledge base.
    """
    p = prompt.strip().lower()
    
    username = ctx.get("username", "there")
    phase = ctx.get("phase_name", "your cycle phase")
    cycle_day = ctx.get("cycle_day", 1)
    days_to_next = ctx.get("days_to_next_period", 0)
    next_period_str = ctx.get("next_period_str", "soon")
    cycle_length = ctx.get("cycle_length_used", 28)
    period_length = ctx.get("period_length", 5)
    fertile_str = ctx.get("fertile_str", "mid-cycle")
    ovulation_str = ctx.get("ovulation_str", "mid-cycle")
    health_factors = ctx.get("health_factors", [])
    care_tips = ctx.get("care_tips", [])
    insights = ctx.get("insights", [])
    predictability = ctx.get("predictability_score", 95)
    
    # Check for greetings
    if any(greet in p for greet in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]):
        factors_mention = f" I see you're managing **{', '.join(health_factors)}**." if health_factors else ""
        return (
            f"Hello {username}! 🌸 I'm your Relax Cycle & Wellness companion.\n\n"
            f"Today you are on **Cycle Day {cycle_day}** in your **{phase}**.{factors_mention}\n\n"
            f"How are you feeling right now? You can ask me anything about:\n"
            f"• 🥗 **Nutrition & meal ideas** for your current phase\n"
            f"• 🩸 **Next period timing** and what to expect\n"
            f"• 💥 **Natural relief for cramps, bloating, or PMS**\n"
            f"• 🦋 **How thyroid or stress influences your cycle**\n"
            f"• 🌱 **Fertility window & ovulation cues**"
        )
    
    # Nutrition / Diet / Food queries
    if any(w in p for w in ["food", "eat", "diet", "nutrition", "meal", "recipe", "snack", "hungry", "craving"]):
        if "menstrual" in phase.lower() or "period" in phase.lower():
            return (
                f"### 🥗 Nutrition Guide: Menstrual Phase (Day {cycle_day})\n\n"
                f"During active bleeding, estrogen and progesterone are at their lowest, and iron is lost through menstrual flow. Here is your targeted nourishment plan:\n\n"
                f"1. **Iron & Ferritin Replenishment:**\n"
                f"   - Lentils, spinach, pumpkin seeds, lean meats, or tofu.\n"
                f"   - Pair with **Vitamin C** (bell peppers, oranges, lemon water) to double non-heme iron absorption.\n\n"
                f"2. **Anti-Cramping Warm Foods:**\n"
                f"   - Bone broth, vegetable soups, turmeric ginger tea, and warm spiced stews.\n"
                f"   - Warmth promotes pelvic blood flow and reduces uterine spasms.\n\n"
                f"3. **Magnesium & Healthy Fats:**\n"
                f"   - Dark chocolate (70%+), avocados, and walnuts help soothe prostaglandins that trigger cramps.\n\n"
                f"⚠️ *Tip:* Minimize excessive caffeine and ultra-salty snacks, as they restrict pelvic microcirculation and worsen water retention."
            )
        elif "follicular" in phase.lower():
            return (
                f"### 🥗 Nutrition Guide: Follicular Phase (Day {cycle_day})\n\n"
                f"Your estrogen levels are steadily rising, bringing higher insulin sensitivity and renewed energy!\n\n"
                f"1. **Fresh & Vibrant Energy:**\n"
                f"   - Light, nutrient-dense whole foods: crisp leafy salads, sprouted grains, berries, and citrus fruits.\n\n"
                f"2. **Healthy Gut & Estrogen Metabolism:**\n"
                f"   - Fermented foods (kimchi, kefir, sauerkraut) support the estrobolome (gut bacteria that regulate estrogen recycling).\n\n"
                f"3. **Lean Proteins:**\n"
                f"   - Eggs, wild-caught salmon, quinoa, and legumes provide amino acids to support ovarian follicle maturation."
            )
        elif "fertile" in phase.lower() or "ovulation" in phase.lower():
            return (
                f"### 🥗 Nutrition Guide: Ovulation & Fertile Window (Day {cycle_day})\n\n"
                f"Your body is experiencing peak estrogen and an LH surge. Your metabolism is running high:\n\n"
                f"1. **Antioxidant & Glutathione Support:**\n"
                f"   - Berries, asparagus, broccoli, and leafy greens protect the developing ovum from oxidative stress.\n\n"
                f"2. **Fiber for Hormonal Clearance:**\n"
                f"   - Flaxseeds and chia seeds bind to excess circulating estrogen in the digestive tract.\n\n"
                f"3. **Hydration & Electrolytes:**\n"
                f"   - Ample water, coconut water, or cucumbers to ensure healthy, fluid cervical mucus."
            )
        else: # Luteal / PMS
            return (
                f"### 🥗 Nutrition Guide: Luteal & Pre-Menstrual Phase (Day {cycle_day})\n\n"
                f"Progesterone dominates, raising your core body temperature and increasing your resting metabolic rate by ~100–300 calories/day:\n\n"
                f"1. **Complex Carbohydrates for Serotonin:**\n"
                f"   - Sweet potatoes, brown rice, oats, and roasted squash prevent sudden blood sugar crashes and PMS irritability.\n\n"
                f"2. **Magnesium & Vitamin B6:**\n"
                f"   - Pumpkin seeds, bananas, dark leafy greens, and almonds help calm the nervous system and decrease pre-menstrual water retention.\n\n"
                f"3. **Herbal Calming:**\n"
                f"   - Chamomile, peppermint, and dandelion root teas encourage liver drainage and digestive ease."
            )
            
    # Next Period / Expected date queries
    if any(w in p for w in ["next period", "when is my period", "when will i get", "countdown", "late", "due", "overdue"]):
        if days_to_next > 0:
            status_txt = f"in **{days_to_next} days** on **{next_period_str}**"
        elif days_to_next == 0:
            status_txt = f"**due today** (**{next_period_str}**)"
        else:
            status_txt = f"**{abs(days_to_next)} days past the estimated date** ({next_period_str})"
            
        factors_line = ""
        if health_factors:
            factors_line = f"\n\n*Note on fluctuations:* Because your profile has **{', '.join(health_factors)}**, your cycle predictability is ~**{predictability}%**, meaning periods can occasionally arrive a few days earlier or later."
            
        return (
            f"### 🩸 Next Period Forecast\n\n"
            f"Based on your historical average cycle length of **{cycle_length} days**, your next period is expected {status_txt}.\n\n"
            f"• **Current Cycle Day:** Day {cycle_day}\n"
            f"• **Current Phase:** {phase}\n"
            f"• **Expected Date:** {next_period_str}{factors_line}\n\n"
            f"💡 *Preparation Tip:* Keep your favorite pads/tampons or menstrual cup handy, and consider having a warm heating pad or magnesium supplement ready."
        )

    # Cramps / Pain / Bloating / Physical Symptoms
    if any(w in p for w in ["cramp", "pain", "bloat", "ache", "sore", "headache", "back pain", "tender", "breast"]):
        return (
            f"### 💥 Relieving Cramps & Discomfort ({phase})\n\n"
            f"Menstrual cramps (dysmenorrhea) are caused by prostaglandins—hormone-like compounds that cause the uterine muscle to contract to shed the lining.\n\n"
            f"Here are proven, gentle ways to find relief:\n\n"
            f"1. **Continuous Low Heat Therapy:**\n"
            f"   - A hot water bottle or heating pad on the lower abdomen or lower back relaxes smooth muscle tissue and promotes blood flow, as effectively as mild analgesics.\n\n"
            f"2. **Targeted Magnesium Glycinate:**\n"
            f"   - Magnesium relaxes smooth muscle fibers and tempers prostaglandin inflammation.\n\n"
            f"3. **Herbal Teas:**\n"
            f"   - **Ginger tea:** Blocks the cyclooxygenase (COX-2) enzyme that produces inflammatory prostaglandins.\n"
            f"   - **Chamomile tea:** Contains glycine, an amino acid that relaxes muscle spasms and soothes tension.\n\n"
            f"4. **Gentle Pelvic Stretches:**\n"
            f"   - Child's Pose (*Balasana*), Cat-Cow, and Reclining Bound Angle pose (*Supta Baddha Konasana*) release pelvic floor tension.\n\n"
            f"⚠️ *When to consult a doctor:* If cramps are debilitating, radiate severely down the legs, or do not respond to common remedies, discuss with your OB/GYN to evaluate conditions like endometriosis or fibroids."
        )

    # Thyroid / Endocrine queries
    if any(w in p for w in ["thyroid", "hypothyroid", "hyperthyroid", "hashimoto", "tsh", "hormone"]):
        return (
            f"### 🦋 Thyroid Health & Your Menstrual Cycle\n\n"
            f"The thyroid gland is your body's metabolic master regulator. It communicates directly with the ovaries via the **Hypothalamic-Pituitary-Ovarian (HPO) axis**:\n\n"
            f"• **Hypothyroidism (Underactive):**\n"
            f"  - Low thyroid hormones (T3/T4) stimulate excess TRH from the hypothalamus, prompting the pituitary to produce elevated TSH and prolactin.\n"
            f"  - Elevated prolactin can suppress GnRH, delaying follicular development and ovulation.\n"
            f"  - *Cycle Impact:* Longer cycle lengths (32–40+ days), missed periods, heavier bleeding (menorrhagia), and lower basal body temperature.\n\n"
            f"• **Hyperthyroidism (Overactive):**\n"
            f"  - Excess thyroid hormones increase sex hormone-binding globulin (SHBG), lowering free active estrogen.\n"
            f"  - *Cycle Impact:* Shorter cycles, lighter or scanty bleeding (hypomenorrhea), and sporadic anovulatory cycles.\n\n"
            f"• **Nourishment Focus:**\n"
            f"  - Selenium (1-2 Brazil nuts/day), Zinc, and adequate clean protein.\n"
            f"  - Cook cruciferous vegetables (broccoli, cabbage) rather than eating them raw to reduce goitrogenic impact."
        )

    # PCOS / Irregularity / Endometriosis
    if any(w in p for w in ["pcos", "pcod", "endometriosis", "endo", "irregular", "fluctuation", "delay"]):
        return (
            f"### 🧬 Understanding Cycle Irregularity & Hormonal Conditions\n\n"
            f"Hormonal balance relies on precise timing between the brain and ovaries:\n\n"
            f"• **PCOS (Polycystic Ovarian Syndrome):**\n"
            f"  - Higher baseline LH and localized ovarian androgens can stall follicle growth. Instead of a single dominant follicle rupturing on Day 14, multiple small follicles develop slowly.\n"
            f"  - *Cycle Impact:* Delayed ovulation, extended follicular phase, cycles ranging from 35 to 60+ days, and unpredictability.\n"
            f"  - *Supportive steps:* Insulin sensitivity support (protein + fiber + healthy fat meals, inositol, spearmint tea).\n\n"
            f"• **Endometriosis:**\n"
            f"  - Tissue similar to the uterine lining grows outside the uterus, triggering localized pelvic inflammation and prostaglandins.\n"
            f"  - *Supportive steps:* Omega-3 fatty acids, curcumin/turmeric, and anti-inflammatory restorative care.\n\n"
            f"Relax incorporates these conditions into its fluctuation engine to provide wider buffer margins and realistic forecasts!"
        )

    # Fertility / Ovulation / Pregnancy chance
    if any(w in p for w in ["fertile", "fertility", "ovulation", "ovulate", "pregnant", "conceive", "conception"]):
        return (
            f"### 🌱 Fertility & Ovulation Window Guide\n\n"
            f"Your fertile window spans approximately 6 days:\n"
            f"• **5 days prior to ovulation:** Sperm can survive in fertile cervical mucus for up to 5 days.\n"
            f"• **Ovulation day (approx. {ovulation_str}):** The egg survives for 12–24 hours post-release.\n\n"
            f"**Your Cycle Estimates:**\n"
            f"• Estimated Fertile Window: **{fertile_str}**\n"
            f"• Estimated Ovulation Day: **{ovulation_str}**\n\n"
            f"**Body Signs of High Fertility:**\n"
            f"1. **Cervical Fluid:** Clear, slippery, and stretchy (like raw egg whites).\n"
            f"2. **Basal Body Temperature:** Slight dip right before ovulation, followed by a sustained 0.3°C–0.5°C rise caused by progesterone.\n"
            f"3. **Libido & Energy:** Natural surge in confidence and energy driven by peak estrogen."
        )

    # Mood / Emotions / Mental wellness
    if any(w in p for w in ["mood", "sad", "anxious", "anxiety", "cry", "irritable", "angry", "depressed", "brain fog", "emotional"]):
        return (
            f"### 🌸 Mental Wellbeing & Cycle Hormones\n\n"
            f"Hormonal shifts directly impact neurotransmitters like **serotonin** and **GABA**:\n\n"
            f"• **In the Luteal/PMS Phase:** Progesterone drops abruptly a few days before your period. This sudden decline can pull serotonin levels down, triggering sadness, irritability, anxiety, or emotional fatigue.\n"
            f"• **In the Follicular Phase:** Estrogen boosts dopamine and serotonin, increasing mental clarity and motivation.\n\n"
            f"**Self-Compassion Strategies:**\n"
            f"1. Remind yourself: *What you are feeling is real, valid, and chemically driven—not a personal failing.*\n"
            f"2. Keep blood sugar steady: Pair protein with complex carbs every 3-4 hours to avoid mood crashes.\n"
            f"3. Reduce sensory overload: Dim lights, step back from high-stakes decisions, and allow yourself extra rest."
        )

    # Fallback / General cycle query
    return (
        f"### 🌸 Relax Cycle Assistant\n\n"
        f"Thank you for sharing, {username}! Here is your current cycle summary:\n\n"
        f"• **Cycle Day:** Day {cycle_day} ({phase})\n"
        f"• **Next Period:** {next_period_str} ({f'in {days_to_next} days' if days_to_next > 0 else 'Due now'})\n"
        f"• **Cycle Length Baseline:** {cycle_length} days\n"
        f"• **Health Factors:** {', '.join(health_factors) if health_factors else 'None recorded'}\n\n"
        f"**Helpful Next Steps:**\n"
        f"1. Ask me for **recipes & foods** suited for {phase}.\n"
        f"2. Log any symptoms or flow in the **📝 Symptoms Update** tab.\n"
        f"3. Ask about **natural cramp relief**, **thyroid effects**, or **ovulation timing**."
    )
