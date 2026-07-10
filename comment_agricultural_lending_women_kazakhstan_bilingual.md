# COMMENT: The Impact of Agricultural Lending on Women’s Entrepreneurship in Kazakhstan’s Agricultural Sector: The Role of Regional Factors and Access to Land

## Original text

### 1 General comments

This paper examines the impact of institutional agricultural lending on women’s entrepreneurship in Kazakhstan’s agricultural sector using regional panel data for 20 regions over the period 2015–2024. The paper combines two-way fixed-effects panel regressions, k-means clustering, and a random forest model to distinguish between correlation, regional heterogeneity, and predictive relationships. The central finding is that agricultural lending is positively correlated with the number of women-owned farms in pooled OLS, but this association disappears after controlling for region and year fixed effects. The paper therefore argues that credit is concentrated in already more developed regions, while limited access to land remains a binding institutional constraint on women’s entrepreneurship in agriculture. The topic is highly relevant for inclusive development, gender-sensitive agricultural policy, and rural finance in transition economies. My specific comments are below.

### 2 Specific comments

#### A. Contribution of the work

The paper addresses an important and under-researched topic: the relationship between agricultural finance, women’s entrepreneurship, and land access in Kazakhstan. The focus on Central Asia is valuable, since much of the existing literature on women farmers, financial inclusion, and land constraints is concentrated on African and South Asian contexts. The paper’s attempt to examine whether credit can compensate for limited land access is also potentially useful and policy relevant.

The paper’s main contribution appears to lie in showing that the positive association between lending and women-owned farms is largely driven by structural differences across regions rather than by a causal within-region effect of lending. This is a useful distinction, especially because many studies of credit and entrepreneurship rely on cross-sectional associations. The comparison between pooled OLS and the two-way fixed-effects model is therefore one of the strongest elements of the paper.

However, the contribution could be sharpened further. The paper should state more clearly whether its primary novelty is empirical, methodological, or policy-oriented. At present, the paper presents three contributions: evidence from Kazakhstan, the three-module empirical framework, and the argument that land access constrains the effect of lending. These are all potentially useful, but the introduction should rank them more clearly and explain exactly how the paper advances the existing literature.

The paper should also be more precise in distinguishing confirmatory findings from genuinely new findings. The claim that land access matters for women farmers is well established in the broader gender and agriculture literature. The paper’s specific contribution is not simply that land matters, but that, in the Kazakhstan context, credit loses significance once regional fixed effects are introduced, while women continue to face very low access to agricultural land. This point should be made more explicitly.

#### B. Methodology & Data

The paper uses an interesting mixed-method empirical strategy, combining panel econometrics, cluster analysis, and machine learning. This structure is promising, but several methodological and data issues require clarification.

- The paper sometimes uses causal language too strongly. The two-way fixed-effects model is an improvement over pooled OLS because it controls for time-invariant regional differences and common year effects. However, it does not fully eliminate endogeneity. Lending may still respond to time-varying regional factors such as changes in agricultural profitability, regional policy priorities, women’s demand for credit, local infrastructure investment, or administrative capacity. The authors should therefore be more cautious in describing the TWFE estimates as causal unless stronger identification assumptions are clearly stated and defended.

- The paper should clarify the exact unit and construction of the lending variables. It is important to know whether the credit measures refer only to loans actually received by women-owned farms, loans to women farmers, or broader regional agricultural lending that includes women beneficiaries. This distinction matters because the interpretation of the coefficient depends on whether the treatment variable directly captures women-specific access to finance.

- The dataset is described as an unbalanced panel with 20 regions over 2015–2024 and 175 observations. The paper should explain more clearly why the full balanced panel would not contain 200 observations, and which years or regions are missing. This is especially important because some regions, including newly formed regions, appear to have incomplete data. A table showing missing observations by variable and year would improve transparency.

- The treatment of missing values requires further discussion. The paper notes that the variable for loans from the Financial Support Fund has around 39% missing values and that the land share variable also has missing values. While fixed-effects models can handle unbalanced panels, missingness may still be non-random. If missing observations are concentrated in particular regions, cities, or newly created administrative units, the estimates may be affected. The authors should discuss whether the missingness is random, institutional, or systematically related to the outcomes being studied.

- The dependent variable is the number of women-owned farms. This is a relevant measure of extensive-margin entrepreneurship, but it does not capture the quality, survival, productivity, profitability, employment generation, or growth of these farms. The paper should acknowledge more clearly that the results apply to the number of women-owned farms rather than to the broader performance of women entrepreneurs. If data are available, additional outcomes such as output, farm survival, land size, income, or productivity would strengthen the analysis.

- The use of log(1 + x) transformations is appropriate given the presence of zeros, but the interpretation of coefficients requires greater care. The paper often treats coefficients as elasticities, which is only an approximation under this transformation and may be misleading when variables contain many zeros or small values. The authors should clarify this point explicitly or report marginal effects in more interpretable terms.

- The specification of the baseline TWFE model should be presented more carefully. The paper appears to estimate a model with region and year fixed effects and clustered standard errors at the regional level. Since there are only 20 regions, inference based on clustered standard errors may be sensitive to the small number of clusters. The authors should consider reporting wild cluster bootstrap p-values or, at minimum, acknowledge the limitation of having only 20 clusters.

- The paper should consider whether lagged credit effects are adequately explored. Credit may not immediately translate into the establishment of a new farm. The paper includes a lagged credit variable in the random forest feature list, but the econometric section should more systematically test contemporaneous and lagged effects. A specification using one-year and possibly two-year lags of credit would help assess whether lending affects women-owned farms with a delay.

- The land access variable is central to the paper’s argument, but its measurement needs more detail. The paper reports the share of agricultural land allocated to women, but it is not clear whether this reflects ownership, use rights, lease rights, registration, or effective control. Since land can operate as both a productive asset and collateral, the institutional meaning of this variable is crucial. The paper should also discuss whether the land is comparable in quality across regions.

- The hypothesis that land access moderates the effect of lending should be tested more directly. The paper states that land access may moderate the effectiveness of credit, but the main econometric results do not appear to include a clearly presented interaction term between credit and land share. A model including log(credit total) × land share would provide a more direct test of this hypothesis. If the interaction is insignificant, that result should also be discussed.

- The comparison between pooled OLS and TWFE is useful, but the interpretation should be refined. The disappearance of the lending coefficient in TWFE shows that the positive pooled relationship is largely cross-sectional. However, this does not necessarily prove that credit is ineffective; it may indicate that within-region changes in credit over the sample period are too limited, measured with error, or affected by timing issues. The authors should distinguish between “no estimated within-region effect” and the broader claim that lending does not work.

- The k-means clustering section is potentially useful, but it needs stronger justification. The paper states that the optimal number of clusters is two based on a silhouette score of 0.400. This value suggests some structure, but not a very strong separation. The authors should report silhouette scores for alternative cluster numbers and provide a clearer rationale for why two clusters are substantively meaningful. It would also help to list the regions included in each cluster.

- The variables used for clustering include the mean and standard deviation of women-owned farms, mean and standard deviation of lending, land share, growth trend, and coefficient of variation. Some of these variables are mechanically related to the outcome and lending variables used elsewhere in the paper. The authors should explain whether the clustering is intended as a descriptive classification rather than an independent validation of the regression results.

- The random forest section should be interpreted with caution. The reported model performance is weak, with a negative R2 under group cross-validation. This indicates that the model performs worse than a simple mean prediction for held-out regions. Given this poor generalisation performance, feature importance should not be used to make strong substantive claims. The random forest results can be retained as exploratory evidence, but the paper should not present them as confirmation of the causal argument.

- The random forest feature importance results appear to give high importance to the Financial Support Fund lending variable. However, this variable also has substantial missingness and a reduced sample. The authors should check whether the high importance reflects genuine predictive content or patterns generated by missing data, regional coverage, or institutional allocation rules.

- The partial dependence plot for land access is interesting, but its interpretation should be more cautious. The paper suggests that a threshold around 2% of land ownership may be important. However, partial dependence plots from a poorly performing random forest model may not provide reliable evidence of a threshold. If the authors wish to claim a threshold effect, they should test it using an econometric model, for example with spline terms or threshold regressions.

- The paper should include more robustness checks. Useful checks would include excluding cities of national importance, excluding newly formed regions, using alternative credit measures, estimating models with lagged credit, testing interactions between credit and land, and reporting results with and without land share to assess the sensitivity of the credit coefficient.

#### C. Other issues

- The title is clear but quite long. The authors may consider shortening it slightly while retaining the three key elements: agricultural lending, women’s entrepreneurship, and land access in Kazakhstan.

- The abstract is informative, but it should be made more concise. It currently includes several methodological details and policy implications. A shorter abstract that clearly states the research question, data, method, main result, and policy implication would improve readability.

- The introduction should better distinguish between the general motivation and the specific research gap. The paper discusses inclusive growth, rural development, and food security, but the precise gap in the Kazakhstan and Central Asian literature should be stated earlier and more directly.

- The hypotheses could be formulated more consistently. Hypothesis H1 is stated as a null-style hypothesis that lending has no statistically significant effect. It may be better to frame the hypotheses in a theoretically motivated way and then test whether the evidence supports or rejects them.

- The literature review is broad, but it could be more focused. The paper cites many recent studies, but the review sometimes reads as a list of claims rather than a structured synthesis. It would be helpful to organise the literature around three clearer themes: financial inclusion, land and institutional constraints, and regional heterogeneity.

- Some parts of the literature review contain overly strong or unclear statements. For example, the discussion of digital finance and artificial intelligence could be shortened unless these issues are directly linked to the empirical analysis. At present, digitalisation is discussed in the literature review, but it is not central to the empirical model.

- The paper should check the accuracy and relevance of all citations. Several citations are very recent, and some claims appear broad. The authors should ensure that each citation directly supports the statement being made and that all references are complete and correctly formatted.

- Figure 1 is useful because it summarises the three-module analytical framework. However, it should be improved visually and conceptually. The figure should make clearer how the three modules relate to the three hypotheses and how the outputs of the modules are integrated in the final interpretation.

- Table 1 is useful, but the formatting needs attention. Some entries and labels appear awkward, for example the word “oprule” appears in the table text. The table should be carefully edited for presentation quality.

- The paper should be consistent in its terminology. It uses terms such as women-owned farms, female-headed farms, women farmers, women entrepreneurs, and female-led enterprises. These may not always mean exactly the same thing. The authors should define the core outcome variable and use consistent terminology throughout.

- The paper should clarify whether “women-owned farms” refers to ownership, management, registration, or farm headship. This distinction is particularly important in gender analysis because formal ownership and effective decision-making power may differ.

- There are some inconsistencies in the interpretation of the results. For example, the paper states that lending does not have a negative effect, when the intended meaning appears to be that lending does not have a statistically significant positive causal effect. This should be corrected to avoid confusion.

- The cluster results are interesting, but the policy interpretation should be more cautious. The paper argues that Cluster 1 has low initial levels but high growth rates. The authors should check whether this simply reflects convergence from a low base rather than evidence of a distinct policy regime.

- The discussion of policy recommendations is relevant, but it should be more directly tied to the empirical findings. The recommendations on gender-sensitive lending, alternative collateral, land rights, and regional infrastructure are sensible, but the paper should distinguish between recommendations directly supported by the results and broader policy suggestions based on the literature.

- The limitations section is welcome but should be strengthened. In particular, the authors should emphasise limitations related to aggregate regional data, measurement of land rights, missing observations, small number of clusters for inference, and the inability of the current design to fully rule out time-varying endogeneity.

- The conclusion should be more concise. It should return to the three hypotheses and state clearly: H1 is supported by the TWFE results; H2 is supported descriptively by the clustering results; and H3 is suggestive but requires a more direct interaction test between lending and land access.

- The authors should provide the full list of regions in the sample and identify which regions belong to each cluster. This would make the regional heterogeneity analysis more transparent and would help readers assess the policy relevance of the cluster classification.

- The paper would benefit from careful language editing. There are several awkward phrases, repeated points, and grammatical issues. Improving the language would make the argument clearer and strengthen the paper’s overall presentation.

I hope the authors find these comments useful.

The referee.

---

## Русский перевод

# КОММЕНТАРИЙ: Влияние сельскохозяйственного кредитования на женское предпринимательство в аграрном секторе Казахстана: роль региональных факторов и доступа к земле

## 1 Общие комментарии

В данной статье рассматривается влияние институционального сельскохозяйственного кредитования на женское предпринимательство в аграрном секторе Казахстана с использованием региональных панельных данных по 20 регионам за период 2015–2024 гг. В работе объединяются панельные регрессии с двусторонними фиксированными эффектами, кластеризация методом k-means и модель случайного леса для разграничения корреляции, региональной неоднородности и прогнозных взаимосвязей. Центральный результат заключается в том, что сельскохозяйственное кредитование положительно коррелирует с числом фермерских хозяйств, принадлежащих женщинам, в объединённой OLS-модели, однако эта связь исчезает после контроля фиксированных эффектов регионов и лет. Следовательно, в статье утверждается, что кредит концентрируется в уже более развитых регионах, тогда как ограниченный доступ к земле остаётся обязательным институциональным ограничением для женского предпринимательства в сельском хозяйстве. Тема является крайне актуальной для инклюзивного развития, гендерно-чувствительной аграрной политики и сельского финансирования в переходных экономиках. Мои конкретные комментарии приведены ниже.

## 2 Конкретные комментарии

### A. Вклад работы

Статья посвящена важной и недостаточно изученной теме: взаимосвязи между сельскохозяйственным финансированием, женским предпринимательством и доступом к земле в Казахстане. Фокус на Центральной Азии представляет ценность, поскольку значительная часть существующей литературы о женщинах-фермерах, финансовой инклюзии и земельных ограничениях сосредоточена на африканском и южноазиатском контекстах. Попытка статьи изучить, может ли кредит компенсировать ограниченный доступ к земле, также является потенциально полезной и значимой с точки зрения политики.

Основной вклад статьи, по-видимому, заключается в демонстрации того, что положительная связь между кредитованием и фермерскими хозяйствами, принадлежащими женщинам, в значительной степени обусловлена структурными различиями между регионами, а не причинным эффектом кредитования внутри региона. Это полезное разграничение, особенно потому, что многие исследования кредита и предпринимательства опираются на кросс-секционные ассоциации. Поэтому сравнение объединённой OLS-модели и модели с двусторонними фиксированными эффектами является одним из наиболее сильных элементов статьи.

Однако вклад работы можно сформулировать более чётко. В статье следует яснее указать, является ли её основная новизна эмпирической, методологической или ориентированной на политику. В настоящее время в статье представлены три вклада: данные по Казахстану, трёхмодульная эмпирическая рамка и аргумент о том, что доступ к земле ограничивает эффект кредитования. Все они потенциально полезны, однако во введении следует более ясно ранжировать их и объяснить, каким именно образом статья продвигает существующую литературу.

Также статье следует точнее различать подтверждающие результаты и действительно новые результаты. Утверждение о том, что доступ к земле важен для женщин-фермеров, уже хорошо закреплено в более широкой литературе по гендеру и сельскому хозяйству. Специфический вклад статьи заключается не просто в том, что земля имеет значение, а в том, что в казахстанском контексте кредит теряет статистическую значимость после введения региональных фиксированных эффектов, тогда как женщины продолжают сталкиваться с крайне низким доступом к сельскохозяйственным землям. Этот тезис следует сформулировать более явно.

### B. Методология и данные

В статье используется интересная эмпирическая стратегия смешанных методов, объединяющая панельную эконометрику, кластерный анализ и машинное обучение. Такая структура выглядит перспективной, однако ряд методологических вопросов и вопросов, связанных с данными, требует уточнения.

- В статье иногда слишком уверенно используется причинно-следственная терминология. Модель с двусторонними фиксированными эффектами является улучшением по сравнению с объединённой OLS-моделью, поскольку она контролирует неизменные во времени региональные различия и общие годовые эффекты. Однако она не устраняет эндогенность полностью. Кредитование всё ещё может реагировать на изменяющиеся во времени региональные факторы, такие как изменения сельскохозяйственной прибыльности, региональные политические приоритеты, спрос женщин на кредит, инвестиции в местную инфраструктуру или административная способность. Поэтому авторам следует быть осторожнее при описании оценок TWFE как причинных, если более сильные идентификационные предпосылки не будут чётко сформулированы и обоснованы.

- В статье следует уточнить точную единицу измерения и способ построения переменных кредитования. Важно понимать, относятся ли кредитные показатели только к займам, фактически полученным фермерскими хозяйствами, принадлежащими женщинам, к займам женщинам-фермерам или к более широкому региональному сельскохозяйственному кредитованию, включающему женщин-бенефициаров. Это различие важно, поскольку интерпретация коэффициента зависит от того, отражает ли переменная воздействия непосредственно специфический доступ женщин к финансированию.

- Набор данных описывается как несбалансированная панель по 20 регионам за 2015–2024 гг. и 175 наблюдениям. В статье следует более ясно объяснить, почему полная сбалансированная панель не содержит 200 наблюдений, а также какие годы или регионы отсутствуют. Это особенно важно, поскольку некоторые регионы, включая недавно созданные регионы, по-видимому, имеют неполные данные. Таблица с пропущенными наблюдениями по переменным и годам повысила бы прозрачность.

- Обработка пропущенных значений требует дополнительного обсуждения. В статье отмечается, что переменная займов из Фонда финансовой поддержки имеет около 39% пропущенных значений, а переменная доли земли также содержит пропуски. Хотя модели с фиксированными эффектами могут работать с несбалансированными панелями, пропуски всё равно могут быть неслучайными. Если отсутствующие наблюдения сконцентрированы в отдельных регионах, городах или недавно созданных административных единицах, оценки могут быть искажены. Авторам следует обсудить, являются ли пропуски случайными, институциональными или систематически связанными с изучаемыми результатами.

- Зависимой переменной является количество фермерских хозяйств, принадлежащих женщинам. Это релевантный показатель предпринимательства по экстенсивной марже, однако он не отражает качество, выживаемость, производительность, прибыльность, создание рабочих мест или рост этих хозяйств. В статье следует яснее признать, что результаты относятся к количеству фермерских хозяйств, принадлежащих женщинам, а не к более широкой эффективности деятельности женщин-предпринимателей. Если данные доступны, дополнительные исходы, такие как объём выпуска, выживаемость хозяйств, размер земельных участков, доход или производительность, усилили бы анализ.

- Использование преобразования log(1 + x) уместно с учётом наличия нулевых значений, однако интерпретация коэффициентов требует большей осторожности. В статье коэффициенты часто трактуются как эластичности, что является лишь приближением при таком преобразовании и может вводить в заблуждение, когда переменные содержат много нулей или малых значений. Авторам следует явно прояснить этот момент или представить предельные эффекты в более интерпретируемой форме.

- Спецификацию базовой модели TWFE следует представить более тщательно. По-видимому, в статье оценивается модель с фиксированными эффектами регионов и лет и кластеризованными стандартными ошибками на региональном уровне. Поскольку регионов всего 20, выводы на основе кластеризованных стандартных ошибок могут быть чувствительны к малому числу кластеров. Авторам следует рассмотреть возможность представления p-значений wild cluster bootstrap или, как минимум, признать ограничение, связанное с наличием только 20 кластеров.

- Статье следует рассмотреть, достаточно ли полно изучены лаговые эффекты кредитования. Кредит может не сразу приводить к созданию нового фермерского хозяйства. В статье лаговая переменная кредита включена в список признаков модели случайного леса, однако эконометрический раздел должен более системно проверять текущие и лаговые эффекты. Спецификация с лагами кредита на один год и, возможно, на два года помогла бы оценить, влияет ли кредитование на фермерские хозяйства, принадлежащие женщинам, с задержкой.

- Переменная доступа к земле является центральной для аргумента статьи, однако её измерение требует более детального описания. В статье указывается доля сельскохозяйственных земель, выделенных женщинам, но не ясно, отражает ли это право собственности, право пользования, аренду, регистрацию или фактический контроль. Поскольку земля может выступать как производственным активом, так и залогом, институциональное значение этой переменной критически важно. В статье также следует обсудить, сопоставимо ли качество земли между регионами.

- Гипотеза о том, что доступ к земле модерирует эффект кредитования, должна быть проверена более напрямую. В статье утверждается, что доступ к земле может модерировать эффективность кредита, однако основные эконометрические результаты, по-видимому, не содержат чётко представленного интеракционного члена между кредитом и долей земли. Модель, включающая log(общий объём кредита) × долю земли, обеспечила бы более прямую проверку этой гипотезы. Если взаимодействие окажется незначимым, этот результат также следует обсудить.

- Сравнение объединённой OLS-модели и TWFE полезно, однако интерпретацию следует уточнить. Исчезновение коэффициента кредитования в TWFE показывает, что положительная объединённая связь в значительной степени является кросс-секционной. Однако это не обязательно доказывает, что кредит неэффективен; это может указывать на то, что изменения кредита внутри региона за рассматриваемый период слишком ограничены, измерены с ошибкой или подвержены проблемам временного лага. Авторам следует различать «отсутствие оценённого эффекта внутри региона» и более широкое утверждение о том, что кредитование не работает.

- Раздел кластеризации k-means потенциально полезен, но требует более сильного обоснования. В статье указано, что оптимальное число кластеров равно двум на основе силуэтного коэффициента 0,400. Это значение указывает на наличие некоторой структуры, но не на очень сильное разделение. Авторам следует представить силуэтные коэффициенты для альтернативного числа кластеров и дать более ясное обоснование, почему два кластера содержательно значимы. Также было бы полезно перечислить регионы, входящие в каждый кластер.

- Переменные, использованные для кластеризации, включают среднее значение и стандартное отклонение числа фермерских хозяйств, принадлежащих женщинам, среднее значение и стандартное отклонение кредитования, долю земли, тренд роста и коэффициент вариации. Некоторые из этих переменных механически связаны с результатом и переменными кредитования, используемыми в других частях статьи. Авторам следует объяснить, предназначена ли кластеризация как описательная классификация, а не как независимая валидация результатов регрессии.

- Раздел со случайным лесом следует интерпретировать осторожно. Сообщаемая производительность модели является слабой: показатель R2 отрицателен при групповой кросс-валидации. Это означает, что модель работает хуже, чем простое предсказание среднего значения для регионов, оставленных вне обучения. С учётом такой слабой обобщающей способности важность признаков не следует использовать для сильных содержательных выводов. Результаты случайного леса можно оставить как разведочное свидетельство, но статья не должна представлять их как подтверждение причинного аргумента.

- Результаты важности признаков в модели случайного леса, по-видимому, придают высокую значимость переменной кредитования из Фонда финансовой поддержки. Однако эта переменная также имеет существенную долю пропусков и сокращённую выборку. Авторам следует проверить, отражает ли высокая важность реальное прогнозное содержание или паттерны, сформированные пропущенными данными, региональным покрытием либо институциональными правилами распределения.

- График частичной зависимости для доступа к земле интересен, однако его интерпретация должна быть более осторожной. В статье предполагается, что порог около 2% владения землёй может быть важным. Однако графики частичной зависимости из модели случайного леса со слабой производительностью могут не давать надёжных доказательств существования порога. Если авторы хотят заявлять о пороговом эффекте, его следует проверить с помощью эконометрической модели, например с использованием сплайн-термов или пороговых регрессий.

- В статье следует включить больше проверок устойчивости. Полезными проверками были бы исключение городов республиканского значения, исключение недавно созданных регионов, использование альтернативных показателей кредита, оценивание моделей с лаговым кредитом, тестирование взаимодействий между кредитом и землёй, а также представление результатов с переменной доли земли и без неё для оценки чувствительности коэффициента кредита.

### C. Прочие вопросы

- Заголовок ясен, но достаточно длинный. Авторы могут рассмотреть возможность его небольшого сокращения при сохранении трёх ключевых элементов: сельскохозяйственное кредитование, женское предпринимательство и доступ к земле в Казахстане.

- Аннотация информативна, но её следует сделать более краткой. Сейчас она включает несколько методологических деталей и политических выводов. Более короткая аннотация, чётко формулирующая исследовательский вопрос, данные, метод, основной результат и политическую импликацию, улучшила бы читаемость.

- Во введении следует лучше разграничить общую мотивацию и конкретный исследовательский пробел. В статье обсуждаются инклюзивный рост, развитие сельских территорий и продовольственная безопасность, однако точный пробел в литературе по Казахстану и Центральной Азии следует обозначить раньше и прямее.

- Гипотезы можно сформулировать более последовательно. Гипотеза H1 представлена как гипотеза в стиле нулевой гипотезы о том, что кредитование не имеет статистически значимого эффекта. Возможно, лучше сформулировать гипотезы теоретически мотивированным образом, а затем проверить, поддерживают ли их данные или опровергают.

- Обзор литературы широк, но его можно сделать более сфокусированным. В статье цитируется много недавних исследований, однако обзор иногда выглядит как перечень утверждений, а не как структурированный синтез. Было бы полезно организовать литературу вокруг трёх более чётких тем: финансовая инклюзия, земельные и институциональные ограничения, а также региональная неоднородность.

- Некоторые части обзора литературы содержат чрезмерно сильные или неясные утверждения. Например, обсуждение цифровых финансов и искусственного интеллекта можно сократить, если эти вопросы не связаны напрямую с эмпирическим анализом. В настоящее время цифровизация обсуждается в обзоре литературы, но не является центральной для эмпирической модели.

- В статье следует проверить точность и релевантность всех цитирований. Несколько источников являются очень недавними, а некоторые утверждения выглядят широкими. Авторам следует убедиться, что каждое цитирование напрямую поддерживает соответствующее утверждение, а все ссылки полны и правильно оформлены.

- Рисунок 1 полезен, поскольку он суммирует трёхмодульную аналитическую рамку. Однако его следует улучшить визуально и концептуально. Рисунок должен яснее показывать, как три модуля соотносятся с тремя гипотезами и как результаты модулей интегрируются в итоговую интерпретацию.

- Таблица 1 полезна, но её форматирование требует внимания. Некоторые элементы и подписи выглядят неудачно, например слово “oprule” встречается в тексте таблицы. Таблицу следует тщательно отредактировать с точки зрения качества представления.

- В статье следует обеспечить терминологическую согласованность. Используются такие термины, как фермерские хозяйства, принадлежащие женщинам, хозяйства, возглавляемые женщинами, женщины-фермеры, женщины-предприниматели и предприятия под женским руководством. Они не всегда могут означать одно и то же. Авторам следует определить ключевую зависимую переменную и последовательно использовать терминологию на протяжении всей статьи.

- В статье следует уточнить, относится ли понятие “women-owned farms” к собственности, управлению, регистрации или главенству в фермерском хозяйстве. Это различие особенно важно в гендерном анализе, поскольку формальное владение и фактическая власть принятия решений могут различаться.

- В интерпретации результатов есть некоторые несогласованности. Например, в статье говорится, что кредитование не имеет отрицательного эффекта, тогда как предполагаемый смысл, по-видимому, заключается в том, что кредитование не имеет статистически значимого положительного причинного эффекта. Это следует исправить во избежание путаницы.

- Результаты кластеризации интересны, но политическая интерпретация должна быть более осторожной. В статье утверждается, что Кластер 1 имеет низкие начальные уровни, но высокие темпы роста. Авторам следует проверить, не отражает ли это просто конвергенцию с низкой базы, а не свидетельство отдельного политического режима.

- Обсуждение политических рекомендаций релевантно, но его следует более напрямую связать с эмпирическими результатами. Рекомендации по гендерно-чувствительному кредитованию, альтернативному залогу, земельным правам и региональной инфраструктуре разумны, однако в статье следует различать рекомендации, непосредственно поддержанные результатами, и более широкие политические предложения, основанные на литературе.

- Раздел ограничений полезен, но его следует усилить. В частности, авторам следует подчеркнуть ограничения, связанные с агрегированными региональными данными, измерением земельных прав, пропущенными наблюдениями, малым числом кластеров для статистического вывода и неспособностью текущего дизайна полностью исключить эндогенность, изменяющуюся во времени.

- Заключение должно быть более кратким. Оно должно вернуться к трём гипотезам и ясно указать: H1 поддерживается результатами TWFE; H2 описательно поддерживается результатами кластеризации; H3 является предположительной, но требует более прямого тестирования взаимодействия между кредитованием и доступом к земле.

- Авторам следует предоставить полный список регионов в выборке и указать, какие регионы относятся к каждому кластеру. Это сделало бы анализ региональной неоднородности более прозрачным и помогло бы читателям оценить политическую релевантность кластерной классификации.

- Статья выиграла бы от тщательного языкового редактирования. В ней есть несколько неудачных формулировок, повторяющихся тезисов и грамматических проблем. Улучшение языка сделало бы аргументацию яснее и усилило бы общую подачу статьи.

Надеюсь, авторы сочтут эти комментарии полезными.

Рецензент.
