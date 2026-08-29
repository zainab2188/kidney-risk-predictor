import gradio as gr
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

# 1. تحميل النموذج والـ Scaler والمصفوفة X
model = tf.keras.models.load_model("model.h5")
scaler = joblib.load("scaler.pkl")
X = joblib.load("X_columns.pkl")  # إذا كان لديكِ ملف يضم أعمدة X أو يمكنكِ تعريفها


def predict_kidney_risk(
    age, bp, sg, al, su, bgr, bu, sc, sod, pot, hemo, pcv, wc
):
  data_dict = {col: 0 for col in X.columns}

  data_dict["age"] = age
  data_dict["bp"] = bp
  data_dict["sg"] = sg
  data_dict["al"] = al
  data_dict["su"] = su
  data_dict["bgr"] = bgr
  data_dict["bu"] = bu
  data_dict["sc"] = sc
  data_dict["sod"] = sod
  data_dict["pot"] = pot
  data_dict["hemo"] = hemo

  for col in X.columns:
    if col.startswith("pcv_") and col.endswith(str(int(pcv))):
      data_dict[col] = 1
    if col.startswith("wc_") and col.endswith(str(int(wc))):
      data_dict[col] = 1

  input_df = pd.DataFrame([data_dict])
  input_scaled = scaler.transform(input_df)

  prediction = model.predict(input_scaled, verbose=0)
  risk_score = float(prediction[0][0])

  # بناء التوصيات الصحية بناءً على الفحوصات المرتفعة
  recommendations = []

  if bp > 90:
    recommendations.append(
        "• ضغط الدم مرتفع: ينصح بتقليل تقليل ملح الصوديوم ومتابعة القراءات"
        " بشكل دوري."
    )
  if sc > 1.2 or bu > 40:
    recommendations.append(
        "• مؤشرات وظائف الكلى (الكرياتينين/اليوريا) مرتفعة: ينصح بمراجعة"
        " طبيب أخصائي إجراء فحوصات دقيقة."
    )
  if al > 0:
    recommendations.append(
        "• وجود زلال (ألبومين) في البول: يستوجب المتابعة للحد من الإجهاد"
        " الكلوي."
    )
  if bgr > 140 or su > 0:
    recommendations.append(
        "• مستويات السكر مرتفعة: يوصى بضبط مستوى الجلوكوز في الدم لحماية"
        " الشعيرات الدموية للكلى."
    )
  if hemo < 11:
    recommendations.append(
        "• انخفاض الهيموجلوبين (فقر دم): يتطلب تقييم طبي للتأكد من استقرار"
        " نسبة الحديد وإفراز نظام الإريثروبويتين."
    )

  # صياغة النتيجة النهائية
  if risk_score > 0.5:
    res = f"⚠️ مستوى الخطر: مرتفع جداً ({risk_score*100:.1f}%)\n"
    res += "--------------------------------------------------\n"
    res += "💡 التوصيات والإرشادات السريرية التوعوية:\n"
    if recommendations:
      res += "\n".join(recommendations)
    else:
      res += "• يُنصح بمراجعة طبيب أخصائي كلى لإجراء الفحوصات التفصيلية."
    return res
  else:
    res = f"✅ مستوى الخطر: منخفض ({risk_score*100:.1f}%)\n"
    res += "--------------------------------------------------\n"
    res += "💡 التوصيات العامة:\n"
    res += (
        "• النتائج الأولية ضمن النطاق الطبيعي. حافظ على نمط حياة صحي وشرب"
        " كميات كافية من الماء يومياً."
    )
    return res


inputs = [
    gr.Slider(minimum=1, maximum=100, value=40, step=1, label="العمر (age)"),
    gr.Slider(minimum=50, maximum=180, value=80, step=5, label="ضغط الدم (bp)"),
    gr.Slider(
        minimum=1.005,
        maximum=1.025,
        value=1.020,
        step=0.005,
        label="الكثافة النوعية (sg) - عشري",
    ),
    gr.Slider(minimum=0, maximum=5, value=0, step=1, label="الألبومين (al)"),
    gr.Slider(minimum=0, maximum=5, value=0, step=1, label="السكر بالبول (su)"),
    gr.Slider(
        minimum=50, maximum=500, value=120, step=1, label="سكر الدم (bgr)"
    ),
    gr.Slider(minimum=10, maximum=200, value=30, step=1, label="اليوريا (bu)"),
    gr.Slider(
        minimum=0.4,
        maximum=15.0,
        value=1.0,
        step=0.1,
        label="الكرياتينين (sc) - عشري",
    ),
    gr.Slider(
        minimum=100, maximum=160, value=138, step=1, label="الصوديوم (sod)"
    ),
    gr.Slider(
        minimum=2.5,
        maximum=8.0,
        value=4.2,
        step=0.1,
        label="البوتاسيوم (pot) - عشري",
    ),
    gr.Slider(
        minimum=3.0,
        maximum=18.0,
value=15.0,
        step=0.1,
        label="الهيموجلوبين (hemo) - عشري",
    ),
    gr.Slider(
        minimum=15, maximum=55, value=44, step=1, label="مكداس الدم (pcv)"
    ),
    gr.Slider(
        minimum=2200,
        maximum=26000,
        value=8400,
        step=100,
        label="كريات الدم البيضاء (wc)",
    ),
]

demo = gr.Interface(
    fn=predict_kidney_risk,
    inputs=inputs,
    outputs="text",
    title="🏥 نظام التنبؤ المبكر بخطر الإصابة بمرض الكلى",
    description=(
        "أداة ذكاء اصطناعي مساعدة للتنبؤ الأولي والتثقيف الصحي برعاية الصحة"
        " العامة."
    ),
)

if __name__ == "__main__":
    demo.launch()