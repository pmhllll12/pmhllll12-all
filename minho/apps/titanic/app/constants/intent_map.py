INTENT_MAP: dict[str, set[str]] = {
    "SURVIVAL_PREDICT": {
        "생존", "사망", "살아남", "죽", "예측", "예상", "확률", "살았", "죽었", "살",
        "survive", "survived", "dead", "alive", "predict", "probability",
    },
    "STATISTICS": {
        "몇", "명", "비율", "평균", "통계", "분포", "총", "전체", "합계",
        "count", "total", "average", "mean", "ratio", "percent", "statistics",
    },
    "PASSENGER_SEARCH": {
        "승객", "이름", "누구", "찾", "검색", "탑승", "인물",
        "passenger", "name", "who", "find", "search",
    },
    "MODEL_TRAIN": {
        "훈련", "학습", "모델", "알고리즘", "정확도", "성능", "테스트",
        "train", "training", "model", "algorithm", "accuracy", "fit", "test",
    },
}
