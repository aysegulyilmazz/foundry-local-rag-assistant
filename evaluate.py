
from rag_utils import find_relevant

TEST_CASES = [
    {"question": "Engelli aileme evde bakım için hangi yardımlar var?", "expected_title": "Engelli Yakını Bakım Yardımı (Evde Bakım Maaşı)"},
    {"question": "KYK bursu nasıl alınır?", "expected_title": "KYK Öğrenim ve Katkı Kredisi"},
    {"question": "İşsizlik ödeneği için kaç gün prim gerekli?", "expected_title": "İşsizlik Ödeneği"},
    {"question": "Doğum yaptım, ne kadar yardım alırım?", "expected_title": "Doğum Yardımı"},
    {"question": "Şehit yakınlarına hangi haklar tanınıyor?", "expected_title": "Şehit ve Gazi Yakınları Aylığı"},
    {"question": "65 yaşındayım ve gelirim yok, yardım alabilir miyim?", "expected_title": "Yaşlılık Aylığı (65 Yaş Aylığı)"},
    {"question": "Çocuğumu okula gönderiyorum, eğitim yardımı var mı?", "expected_title": "Şartlı Eğitim ve Sağlık Yardımı"},
    {"question": "Askerdeyim, ailem geçim sıkıntısı yaşıyor", "expected_title": "Muhtaç Asker Ailesi Yardımı"},
    {"question": "Yeni bir iş kurmak istiyorum, genç girişimci desteği var mı?", "expected_title": "Genç İşçi ve Genç Girişimci Destekleri"},
    {"question": "En iyi pizza tarifi nedir?", "expected_title": None},  # alakasız soru - hicbir sey donmemeli
]


def run_evaluation():
    correct = 0
    total = len(TEST_CASES)

    print("=" * 60)
    print("RETRIEVAL DEĞERLENDİRME RAPORU")
    print("=" * 60)

    for i, case in enumerate(TEST_CASES, 1):
        results = find_relevant(case["question"], top_k=2)
        top_titles = [r["title"] for r in results] if results else []
        top_score = results[0]["score"] if results else 0

        if case["expected_title"] is None:
            passed = top_score < 0.45
            status = "✓ DOĞRU (alakasız olarak tanındı)" if passed else "✗ YANLIŞ (alakasız soruya belge buldu)"
        else:
            passed = case["expected_title"] in top_titles
            status = "✓ DOĞRU" if passed else "✗ YANLIŞ"

        if passed:
            correct += 1

        print(f"\n[{i}/{total}] Soru: {case['question']}")
        print(f"  Beklenen: {case['expected_title'] or '(alakasız)'}")
        print(f"  Bulunan: {top_titles} (skor: {top_score:.2f})")
        print(f"  {status}")

    print("\n" + "=" * 60)
    print(f"SONUÇ: {correct}/{total} doğru (%{100*correct/total:.0f} başarı oranı)")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()