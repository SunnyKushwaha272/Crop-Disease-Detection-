# ─────────────────────────────────────────────────────────────────────────────
# class_names — raw model output names (used for DB queries and model output)
# ─────────────────────────────────────────────────────────────────────────────

class_names = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy"
]


# ─────────────────────────────────────────────────────────────────────────────
# disease_info — keyed by RAW class name so app.py lookup always works:
#   info = disease_info.get(predicted_class, {})
#
# OLD BUG: keys were human names like "Early Blight" but predicted_class
# is always a raw name like "Tomato_Early_blight" → .get() returned {}
# every time → description and treatment were always blank on result page
# and history page.
# ─────────────────────────────────────────────────────────────────────────────

disease_info = {

    # ── POTATO ───────────────────────────────────────────────────────────────

    "Potato___Early_blight": {
        "description":
            "Early blight is a fungal disease caused by Alternaria solani. "
            "It usually affects older leaves first and creates brown spots with concentric rings. "
            "(अर्ली ब्लाइट एक फंगल रोग है जो पत्तियों पर गोल भूरे धब्बे बनाता है।)",
        "treatment":
            "Remove infected leaves, practice crop rotation, and apply fungicides such as chlorothalonil if needed. "
            "(संक्रमित पत्तियों को हटाएँ और आवश्यकता होने पर फफूंदनाशक का उपयोग करें।)"
    },

    "Potato___Late_blight": {
        "description":
            "Late blight is caused by Phytophthora infestans and spreads quickly in cool and wet conditions. "
            "It creates large dark lesions on leaves. "
            "(लेट ब्लाइट ठंडे और नम मौसम में तेजी से फैलता है और पत्तियों पर बड़े काले धब्बे बनाता है।)",
        "treatment":
            "Remove infected plants immediately and apply recommended fungicides like mancozeb. "
            "Avoid overhead watering. "
            "(संक्रमित पौधों को हटाएँ और मैंकोजेब जैसे फफूंदनाशक का उपयोग करें।)"
    },

    "Potato___healthy": {
        "description":
            "The plant leaf appears healthy with no visible disease symptoms. "
            "(पत्ती स्वस्थ दिख रही है और कोई रोग के लक्षण नहीं हैं।)",
        "treatment":
            "Maintain proper irrigation, nutrition, and regular monitoring to keep plants healthy. "
            "(पौधों को स्वस्थ रखने के लिए सही सिंचाई और पोषण बनाए रखें।)"
    },

    # ── TOMATO ───────────────────────────────────────────────────────────────

    "Tomato_Bacterial_spot": {
        "description":
            "Bacterial spot is caused by Xanthomonas bacteria and appears as small dark spots on leaves and fruits. "
            "(बैक्टीरियल स्पॉट एक जीवाणु रोग है जो पत्तियों और फलों पर छोटे काले धब्बे बनाता है।)",
        "treatment":
            "Use disease-free seeds, remove infected plants, and apply copper-based bactericides. "
            "(रोग मुक्त बीज का उपयोग करें और कॉपर आधारित बैक्टीरिसाइड का उपयोग करें।)"
    },

    "Tomato_Early_blight": {
        "description":
            "Early blight is a fungal disease caused by Alternaria solani. "
            "It usually affects older leaves first and creates brown spots with concentric rings. "
            "(अर्ली ब्लाइट एक फंगल रोग है जो पत्तियों पर गोल भूरे धब्बे बनाता है।)",
        "treatment":
            "Remove infected leaves, practice crop rotation, and apply fungicides such as chlorothalonil if needed. "
            "(संक्रमित पत्तियों को हटाएँ और आवश्यकता होने पर फफूंदनाशक का उपयोग करें।)"
    },

    "Tomato_Late_blight": {
        "description":
            "Late blight is caused by Phytophthora infestans and spreads quickly in cool and wet conditions. "
            "It creates large dark lesions on leaves. "
            "(लेट ब्लाइट ठंडे और नम मौसम में तेजी से फैलता है और पत्तियों पर बड़े काले धब्बे बनाता है।)",
        "treatment":
            "Remove infected plants immediately and apply recommended fungicides like mancozeb. "
            "Avoid overhead watering. "
            "(संक्रमित पौधों को हटाएँ और मैंकोजेब जैसे फफूंदनाशक का उपयोग करें।)"
    },

    "Tomato_Leaf_Mold": {
        "description":
            "Leaf mold is a fungal disease that appears as yellow spots on the upper leaf surface and mold on the underside. "
            "(लीफ मोल्ड पत्तियों पर पीले धब्बे और नीचे फफूंदी बनाता है।)",
        "treatment":
            "Improve air circulation, reduce humidity, and apply fungicides when necessary. "
            "(हवा का प्रवाह बढ़ाएँ और आवश्यकता होने पर फफूंदनाशक का उपयोग करें।)"
    },

    "Tomato_Septoria_leaf_spot": {
        "description":
            "Septoria leaf spot causes small circular spots with dark borders on tomato leaves. "
            "(सेप्टोरिया लीफ स्पॉट पत्तियों पर छोटे गोल धब्बे बनाता है।)",
        "treatment":
            "Remove infected leaves and apply fungicides like chlorothalonil or copper sprays. "
            "(संक्रमित पत्तियों को हटाएँ और फफूंदनाशक स्प्रे करें।)"
    },

    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "description":
            "Spider mites are tiny pests that damage leaves by sucking plant sap and causing yellow or speckled leaves. "
            "(स्पाइडर माइट्स छोटे कीट होते हैं जो पत्तियों को नुकसान पहुँचाते हैं।)",
        "treatment":
            "Spray water to reduce mites and apply neem oil or miticides if infestation is severe. "
            "(नीम तेल या माइटिसाइड का उपयोग करें।)"
    },

    "Tomato__Target_Spot": {
        "description":
            "Target spot is a fungal disease that causes circular lesions with concentric rings on leaves. "
            "(टारगेट स्पॉट पत्तियों पर गोल धब्बे बनाता है।)",
        "treatment":
            "Use resistant varieties and apply fungicides when required. "
            "(प्रतिरोधी किस्में उगाएँ और फफूंदनाशक का उपयोग करें।)"
    },

    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "description":
            "Tomato yellow leaf curl virus causes curling and yellowing of leaves and reduces plant growth. "
            "(येलो लीफ कर्ल वायरस पत्तियों को पीला और मुड़ा हुआ बना देता है।)",
        "treatment":
            "Control whiteflies, remove infected plants, and use resistant tomato varieties. "
            "(सफेद मक्खी को नियंत्रित करें और संक्रमित पौधों को हटाएँ।)"
    },

    "Tomato__Tomato_mosaic_virus": {
        "description":
            "Tomato mosaic virus causes mottled patterns on leaves and reduces plant productivity. "
            "(टोमैटो मोज़ेक वायरस पत्तियों पर धब्बेदार पैटर्न बनाता है।)",
        "treatment":
            "Remove infected plants and disinfect tools to prevent spread. "
            "(संक्रमित पौधों को हटाएँ और उपकरणों को साफ रखें।)"
    },

    "Tomato_healthy": {
        "description":
            "The plant leaf appears healthy with no visible disease symptoms. "
            "(पत्ती स्वस्थ दिख रही है और कोई रोग के लक्षण नहीं हैं।)",
        "treatment":
            "Maintain proper irrigation, nutrition, and regular monitoring to keep plants healthy. "
            "(पौधों को स्वस्थ रखने के लिए सही सिंचाई और पोषण बनाए रखें।)"
    },

}