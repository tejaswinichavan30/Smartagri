# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace predict_leaf_disease function
old_func_marker = "def predict_leaf_disease(image_path, crop_type='general'):"
end_func_marker = "# ===============================\n# Helper Function"

new_predict_func = '''def predict_leaf_disease(image_path, crop_type='tomato'):
    # Pre-validate if image contains an actual plant leaf
    if validate_plant_image:
        val_res = validate_plant_image(image_path)
        if not val_res.get('is_plant', True):
            reason = val_res.get('reason', 'No plant leaf detected in the photo.')
            print(f"[predict_leaf_disease] Invalid non-plant image rejected: {reason}")
            return ("Invalid", reason, 0.0)

    crop_key = translations.normalize_disease_crop(crop_type)
    if not crop_key or not translations.is_disease_diagnosis_supported(crop_key):
        print(f"[predict_leaf_disease] Refused unsupported/reference crop: '{crop_type}'")
        return ("Unsupported", crop_type, 0.0)

    crop_info = translations.get_crop_support(crop_key)
    crop_status = crop_info.get('status', 'reference_only')

    # General PlantVillage 49-class CNN
    img = image.load_img(image_path, target_size=(128, 128))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = general_disease_model.predict(img_array)[0]

    # Map normalized crop_key to exact matching prefix in general_disease_classes
    CROP_CLASS_PREFIXES = {
        'apple': 'Apple - ',
        'blueberry': 'Blueberry - ',
        'cherry': 'Cherry including sour - ',
        'corn': 'Corn maize - ',
        'grape': 'Grape - ',
        'orange': 'Orange - ',
        'peach': 'Peach - ',
        'pepper': 'Pepper, bell - ',
        'potato': 'Potato - ',
        'raspberry': 'Raspberry - ',
        'rice': 'Rice - ',
        'soybean': 'Soybean - ',
        'squash': 'Squash - ',
        'strawberry': 'Strawberry - ',
        'tomato': 'Tomato - ',
        'wheat': 'Wheat - '
    }
    prefix = CROP_CLASS_PREFIXES.get(crop_key)
    if not prefix:
        matching_indices = [
            i for i, c in enumerate(general_disease_classes)
            if c.lower().startswith(crop_key)
        ]
    else:
        matching_indices = [
            i for i, c in enumerate(general_disease_classes)
            if c.startswith(prefix)
        ]

    if not matching_indices:
        return ("Unsupported", crop_key, 0.0)

    # 1. Compute total softmax probability on selected crop's classes
    crop_total_prob = float(sum(prediction[i] for i in matching_indices))
    print(f"[predict_leaf_disease] Crop '{crop_key}' total probability: {crop_total_prob:.4f}")

    if crop_total_prob < translations.CROP_MATCH_THRESHOLD:
        print(f"[predict_leaf_disease] Photo doesn't match crop '{crop_key}' (prob {crop_total_prob:.4f} < {translations.CROP_MATCH_THRESHOLD})")
        return ("CropMismatch", crop_key, round(crop_total_prob * 100, 2))

    # 2. Handle disease_only crops (Orange and Squash)
    if crop_status == 'disease_only':
        disease_idx = matching_indices[0]
        prob = float(prediction[disease_idx])
        conf_pct = round(prob * 100, 2)
        if crop_key == 'orange':
            if prob >= translations.DISEASE_CONFIDENCE_THRESHOLD:
                print(f"[predict_leaf_disease] Orange - Citrus greening suspected ({conf_pct}%)")
                return ("Orange", "Huanglongbing (Citrus Greening)", conf_pct)
            else:
                print(f"[predict_leaf_disease] Orange - Citrus greening not detected (prob {conf_pct}%)")
                return ("Orange", "DiseaseNotDetected", conf_pct)
        elif crop_key == 'squash':
            if prob >= translations.DISEASE_CONFIDENCE_THRESHOLD:
                print(f"[predict_leaf_disease] Squash - Powdery mildew suspected ({conf_pct}%)")
                return ("Squash", "Powdery Mildew", conf_pct)
            else:
                print(f"[predict_leaf_disease] Squash - Powdery mildew not detected (prob {conf_pct}%)")
                return ("Squash", "DiseaseNotDetected", conf_pct)

    # 3. Handle full and healthy_only crops
    # Sort matching indices by prediction probability descending
    sorted_indices = sorted(matching_indices, key=lambda i: prediction[i], reverse=True)
    idx1 = sorted_indices[0]
    p1 = float(prediction[idx1])
    p2 = float(prediction[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
    conf_pct = round(p1 * 100, 2)

    # Check confidence threshold and margin
    has_confidence = p1 >= translations.DISEASE_CONFIDENCE_THRESHOLD
    has_margin = (p1 - p2) >= translations.MIN_CONFIDENCE_MARGIN if len(sorted_indices) > 1 else True

    if not has_confidence or not has_margin:
        print(f"[predict_leaf_disease] Uncertain diagnosis for '{crop_key}' (p1={p1:.4f}, p2={p2:.4f}, margin={p1-p2:.4f})")
        return ("Uncertain", crop_key, conf_pct)

    predicted_class = general_disease_classes[idx1]
    print(f"Predicted Disease: {predicted_class} with absolute confidence {conf_pct}%")

    if " - " in predicted_class:
        pred_crop, pred_disease = predicted_class.split(" - ", 1)
    else:
        pred_crop, pred_disease = crop_key, predicted_class

    return (
        pred_crop.strip().title(),
        pred_disease.strip(),
        conf_pct
    )
'''

start_idx = code.find(old_func_marker)
end_idx = code.find(end_func_marker)

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + new_predict_func + "\n" + code[end_idx:]
    print("Updated predict_leaf_disease in app.py")
else:
    print("Could not find predict_leaf_disease markers")

# Replace predict_disease route and api_crop_disease_samples
route_start_marker = "@app.route('/predict_disease', methods=['POST'])"
route_end_marker = "# Smart Irrigation Agent Route"

new_routes = '''@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    try:
        lang = request.form.get('lang', session.get('lang', 'en'))
        session['lang'] = lang

        if 'image' not in request.files:
            return redirect('/')

        file = request.files['image']
        if file.filename == '':
            return redirect('/')

        crop_type = request.form.get('crop_type', 'tomato')
        session['disease_form_data'] = {'crop_type': crop_type}

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, file.filename)
        file.save(filepath)

        predicted_crop, predicted_disease, confidence = predict_leaf_disease(filepath, crop_type)
        print(f"Prediction: {predicted_crop} : {predicted_disease} (Confidence: {confidence}%)")

        if predicted_crop == "Unsupported" or not translations.is_disease_diagnosis_supported(crop_type):
            unsupp_msg = translations.get_crop_support_notice(crop_type, lang)
            unsupp_en = translations.get_crop_support_notice(crop_type, 'en')
            unsupp_kn = translations.get_crop_support_notice(crop_type, 'kn')
            unsupp_hi = translations.get_crop_support_notice(crop_type, 'hi')

            session["predicted_crop"] = "Unsupported"
            session["predicted_disease"] = "Diagnosis Not Available"
            session["disease_confidence"] = 0.0
            session["disease_result_en"] = unsupp_en
            session["disease_result_kn"] = unsupp_kn
            session["disease_result_hi"] = unsupp_hi
            session["disease_result"] = unsupp_msg
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'unsupported',
                    'is_supported': False,
                    'is_valid_leaf': True,
                    'crop': crop_type,
                    'disease': 'Diagnosis Not Available',
                    'confidence': 0.0,
                    'error': unsupp_en,
                    'result': unsupp_en,
                    'result_kn': unsupp_kn,
                    'result_hi': unsupp_hi,
                    'image_path': filepath
                })

            return render_template(
                "index.html",
                **get_session_data()
            )

        if predicted_crop == "Invalid":
            err_en = f"❌ Invalid Image: {predicted_disease}"
            err_kn = f"❌ ಅಮಾನ್ಯ ಫೋಟೋ: ಬೆಳೆ ಅಥವಾ ಎಲೆ ಪತ್ತೆಯಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ಗಿಡದ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
            err_hi = f"❌ अमान्य फोटो: फसल या पत्ती नहीं मिली। कृपया पौधे की पत्ती की स्पष्ट फोटो अपलोड करें।"

            session["predicted_crop"] = "Invalid"
            session["predicted_disease"] = predicted_disease
            session["disease_confidence"] = 0.0
            session["disease_result_en"] = err_en
            session["disease_result_kn"] = err_kn
            session["disease_result_hi"] = err_hi
            session["disease_result"] = err_kn if lang == 'kn' else (err_hi if lang == 'hi' else err_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'error',
                    'is_valid_leaf': False,
                    'crop': 'Invalid',
                    'disease': predicted_disease,
                    'confidence': 0.0,
                    'error': err_en,
                    'result': err_en,
                    'result_kn': err_kn,
                    'result_hi': err_hi,
                    'image_path': filepath
                }), 400

            return render_template(
                "index.html",
                **get_session_data()
            )

        if predicted_crop == "CropMismatch":
            c_name_en = translations.get_crop_name(crop_type, 'en')
            c_name_kn = translations.get_crop_name(crop_type, 'kn')
            c_name_hi = translations.get_crop_name(crop_type, 'hi')

            mismatch_en = translations.DISEASE_PANEL_TEXTS['crop_mismatch_message']['en'].format(crop=c_name_en)
            mismatch_kn = translations.DISEASE_PANEL_TEXTS['crop_mismatch_message']['kn'].format(crop=c_name_kn)
            mismatch_hi = translations.DISEASE_PANEL_TEXTS['crop_mismatch_message']['hi'].format(crop=c_name_hi)

            session["predicted_crop"] = "CropMismatch"
            session["predicted_disease"] = "Crop Mismatch"
            session["disease_confidence"] = 0.0
            session["disease_result_en"] = mismatch_en
            session["disease_result_kn"] = mismatch_kn
            session["disease_result_hi"] = mismatch_hi
            session["disease_result"] = mismatch_kn if lang == 'kn' else (mismatch_hi if lang == 'hi' else mismatch_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'crop_mismatch',
                    'is_valid_leaf': False,
                    'is_crop_match': False,
                    'crop': crop_type,
                    'disease': 'Crop Mismatch',
                    'confidence': 0.0,
                    'error': mismatch_en,
                    'result': mismatch_en,
                    'result_kn': mismatch_kn,
                    'result_hi': mismatch_hi,
                    'image_path': filepath
                }), 400

            return render_template(
                "index.html",
                **get_session_data()
            )

        if predicted_crop == "Uncertain":
            uncert_en = translations.DISEASE_PANEL_TEXTS['uncertain_diagnosis_message']['en']
            uncert_kn = translations.DISEASE_PANEL_TEXTS['uncertain_diagnosis_message']['kn']
            uncert_hi = translations.DISEASE_PANEL_TEXTS['uncertain_diagnosis_message']['hi']

            session["predicted_crop"] = crop_type
            session["predicted_disease"] = "Uncertain"
            session["disease_confidence"] = confidence
            session["disease_result_en"] = uncert_en
            session["disease_result_kn"] = uncert_kn
            session["disease_result_hi"] = uncert_hi
            session["disease_result"] = uncert_kn if lang == 'kn' else (uncert_hi if lang == 'hi' else uncert_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'uncertain',
                    'is_valid_leaf': True,
                    'is_confident': False,
                    'crop': crop_type,
                    'disease': 'Uncertain',
                    'confidence': confidence,
                    'error': uncert_en,
                    'result': uncert_en,
                    'result_kn': uncert_kn,
                    'result_hi': uncert_hi,
                    'image_path': filepath
                })

            return render_template(
                "index.html",
                **get_session_data()
            )

        # Handle Orange (Citrus Greening only)
        if predicted_crop.lower() == "orange":
            session["predicted_crop"] = "Orange"
            session["predicted_disease"] = predicted_disease
            session["disease_confidence"] = confidence

            if predicted_disease == "DiseaseNotDetected":
                o_msg_en = translations.DISEASE_PANEL_TEXTS['orange_not_detected_message']['en']
                o_msg_kn = translations.DISEASE_PANEL_TEXTS['orange_not_detected_message']['kn']
                o_msg_hi = translations.DISEASE_PANEL_TEXTS['orange_not_detected_message']['hi']
            else:
                o_msg_en = f"{translations.DISEASE_PANEL_TEXTS['orange_detected_message']['en']} ({confidence:.1f}% confidence)"
                o_msg_kn = f"{translations.DISEASE_PANEL_TEXTS['orange_detected_message']['kn']} ({confidence:.1f}% ವಿಶ್ವಾಸಾರ್ಹತೆ)"
                o_msg_hi = f"{translations.DISEASE_PANEL_TEXTS['orange_detected_message']['hi']} ({confidence:.1f}% सटीकता)"

            session["disease_result_en"] = o_msg_en
            session["disease_result_kn"] = o_msg_kn
            session["disease_result_hi"] = o_msg_hi
            session["disease_result"] = o_msg_kn if lang == 'kn' else (o_msg_hi if lang == 'hi' else o_msg_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'success',
                    'is_valid_leaf': True,
                    'is_confident': True,
                    'crop': 'Orange',
                    'disease': predicted_disease,
                    'confidence': confidence,
                    'result': o_msg_en,
                    'result_kn': o_msg_kn,
                    'result_hi': o_msg_hi,
                    'image_path': filepath
                })

            return render_template("index.html", **get_session_data())

        # Handle Squash (Powdery Mildew only)
        elif predicted_crop.lower() == "squash":
            session["predicted_crop"] = "Squash"
            session["predicted_disease"] = predicted_disease
            session["disease_confidence"] = confidence

            if predicted_disease == "DiseaseNotDetected":
                s_msg_en = translations.DISEASE_PANEL_TEXTS['squash_not_detected_message']['en']
                s_msg_kn = translations.DISEASE_PANEL_TEXTS['squash_not_detected_message']['kn']
                s_msg_hi = translations.DISEASE_PANEL_TEXTS['squash_not_detected_message']['hi']
            else:
                s_msg_en = f"{translations.DISEASE_PANEL_TEXTS['squash_detected_message']['en']} ({confidence:.1f}% confidence)"
                s_msg_kn = f"{translations.DISEASE_PANEL_TEXTS['squash_detected_message']['kn']} ({confidence:.1f}% ವಿಶ್ವಾಸಾರ್ಹತೆ)"
                s_msg_hi = f"{translations.DISEASE_PANEL_TEXTS['squash_detected_message']['hi']} ({confidence:.1f}% सटीकता)"

            session["disease_result_en"] = s_msg_en
            session["disease_result_kn"] = s_msg_kn
            session["disease_result_hi"] = s_msg_hi
            session["disease_result"] = s_msg_kn if lang == 'kn' else (s_msg_hi if lang == 'hi' else s_msg_en)
            session['uploaded_image'] = filepath

            if request.headers.get('Accept') == 'application/json' or request.is_json:
                return jsonify({
                    'status': 'success',
                    'is_valid_leaf': True,
                    'is_confident': True,
                    'crop': 'Squash',
                    'disease': predicted_disease,
                    'confidence': confidence,
                    'result': s_msg_en,
                    'result_kn': s_msg_kn,
                    'result_hi': s_msg_hi,
                    'image_path': filepath
                })

            return render_template("index.html", **get_session_data())

        # Standard Diagnosis Success
        session["predicted_crop"] = predicted_crop
        session["predicted_disease"] = predicted_disease
        session["disease_confidence"] = confidence

        dis_en = translations.get_disease_translation(predicted_crop, predicted_disease, 'en')
        dis_kn = translations.get_disease_translation(predicted_crop, predicted_disease, 'kn')
        dis_hi = translations.get_disease_translation(predicted_crop, predicted_disease, 'hi')

        dis_result_en = f"Disease Prediction: {dis_en} (Confidence: {confidence:.2f}%)"
        dis_result_kn = f"ರೋಗ ಪತ್ತೆ ಫಲಿತಾಂಶ: {dis_kn} (ವಿಶ್ವಾಸಾರ್ಹತೆ: {confidence:.2f}%)"
        dis_result_hi = f"रोग पहचान परिणाम: {dis_hi} (सटीकता: {confidence:.2f}%)"

        session["disease_result_en"] = dis_result_en
        session["disease_result_kn"] = dis_result_kn
        session["disease_result_hi"] = dis_result_hi
        session["disease_result"] = dis_result_kn if lang == 'kn' else (dis_result_hi if lang == 'hi' else dis_result_en)

        session['uploaded_image'] = filepath

        if request.headers.get('Accept') == 'application/json' or request.is_json:
            return jsonify({
                'status': 'success',
                'is_valid_leaf': True,
                'is_confident': True,
                'crop': predicted_crop,
                'disease': predicted_disease,
                'confidence': confidence,
                'result': dis_result_en,
                'result_kn': dis_result_kn,
                'result_hi': dis_result_hi,
                'image_path': filepath
            })

        return render_template(
            "index.html",
            **get_session_data()
        )

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api/disease_crops', methods=['GET'])
def api_disease_crops():
    lang = request.args.get('lang') or session.get('lang', 'en')
    grouped = translations.get_disease_crops_grouped(lang)
    coverage_line = translations.get_disease_coverage_line(lang)
    panel_texts = {}
    for k, v in translations.DISEASE_PANEL_TEXTS.items():
        if isinstance(v, dict):
            panel_texts[k] = v.get(lang, v.get('en', ''))
        else:
            panel_texts[k] = str(v)
    return jsonify({
        'status': 'success',
        'groups': grouped,
        'coverage_line': coverage_line,
        'panel_texts': panel_texts
    })

@app.route('/api/crop_disease_samples', methods=['GET', 'POST'])
def api_crop_disease_samples():
    crop = request.args.get('crop') or request.form.get('crop') or session.get('recommended_crop') or 'Soybean'
    lang = request.args.get('lang') or request.form.get('lang') or session.get('lang', 'en')
    samples = translations.get_crop_disease_samples(crop, lang)
    is_supp = translations.is_disease_diagnosis_supported(crop)
    notice = translations.get_crop_support_notice(crop, lang)
    coverage_line = translations.get_disease_coverage_line(lang)
    return jsonify({
        'status': 'success',
        'crop': crop,
        'is_diagnosis_supported': is_supp,
        'samples': samples,
        'notice': notice,
        'coverage_line': coverage_line
    })

# ===============================
'''

r_start = code.find(route_start_marker)
r_end = code.find(route_end_marker)

if r_start != -1 and r_end != -1:
    code = code[:r_start] + new_routes + "\n# " + code[r_end:]
    print("Updated routes in app.py")
else:
    print("Could not find route markers")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied updates to app.py successfully.")
