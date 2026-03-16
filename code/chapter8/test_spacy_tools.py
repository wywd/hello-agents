import spacy
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="spacy")

# 加载中文轻量模型（确保已下载：python -m spacy download zh_core_web_sm）
nlp = spacy.load("zh_core_web_sm")

# 待演示的中文句子
text = "马斯克在2024年3月16日于北京中关村以440亿美元收购了推特中国分部。"

# 处理文本（触发所有默认管道）
doc = nlp(text)

# ==================== 1. 查看管道组件 ====================
print("=== 1. 当前加载的管道组件 ===")
print(nlp.pipe_names)
print("-" * 50)

# ==================== 2. 分词 + 词性标注 + 词形还原 ====================
print("=== 2. 分词 + 词性标注 + 词形还原 ===")
print(f"{'Token(分词)':<10} {'POS(词性)':<8} {'POS解释':<20} {'Lemma(词形还原)':<10}")
print("-" * 60)
for token in doc:
    # 解释词性标签
    pos_explain = spacy.explain(token.pos_) or "无解释"
    print(f"{token.text:<10} {token.pos_:<8} {pos_explain:<20} {token.lemma_:<10}")
print("-" * 50)

# ==================== 3. 依存句法分析 ====================
print("=== 3. 依存句法分析 ===")
print(f"{'Token(分词)':<10} {'Dep(依存关系)':<12} {'Head(核心词)':<10} {'Dep解释':<20}")
print("-" * 60)
for token in doc:
    dep_explain = spacy.explain(token.dep_) or "无解释"
    print(f"{token.text:<10} {token.dep_:<12} {token.head.text:<10} {dep_explain:<20}")
print("-" * 50)

# ==================== 4. 命名实体识别（NER） ====================
print("=== 4. 命名实体识别（NER） ===")
print(f"{'实体文本':<15} {'实体类型':<10} {'实体类型解释':<20}")
print("-" * 50)
for ent in doc.ents:
    ent_explain = spacy.explain(ent.label_) or "无解释"
    print(f"{ent.text:<15} {ent.label_:<10} {ent_explain:<20}")
print("-" * 50)

# ==================== 5. 句子分割（单句/多句演示） ====================
print("=== 5. 句子分割（扩展多句演示） ===")
# 扩展为多句，测试分句能力
multi_text = "马斯克在2024年3月16日于北京中关村收购了推特中国分部。该交易金额达440亿美元，是科技行业最大收购案之一。"
multi_doc = nlp(multi_text)
for i, sent in enumerate(multi_doc.sents, 1):
    print(f"第{i}句：{sent.text}")
print("-" * 50)

# ==================== 6. 可选：可视化（依存关系/NER） ====================
# 运行后浏览器打开 http://localhost:5000 查看
from spacy import displacy
# 可视化依存关系
displacy.serve(doc, style="dep", options={"compact": True, "font": "SimHei"}, auto_select_port=True)
# 可视化NER
displacy.serve(doc, style="ent", options={"font": "SimHei"}, auto_select_port=True)