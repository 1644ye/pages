from pathlib import Path
root=Path(__file__).parent
p=root/'dist/generator.js';s=p.read_text(encoding='utf8')
changes={
"const brand=e(v.brand),profile=localProfile(v),product=profile.name;":"const profile=localProfile(v),product=profile.name;",
"section(`Welcome to ${brand}`,":"section('Thoughtful choices for everyday life',",
"At ${brand}, our focus is ${profile.focus}.":"Our approach centers on ${profile.focus}.",
"text.replaceAll('{brand}',brand).replaceAll('{product}',product)":"text.replaceAll('{product}',product)",
"thank you for spending a little of your day with ${brand}.":"thank you for taking the time to explore our collection.",
"If a question comes up along the way, ${contact}":"Questions are welcome at any stage. ${contact}",
"At ${brand}, customer service is here to help with product questions, order details, delivery concerns, and returns.":"Our customer service team can help with product questions, order details, delivery concerns, and returns.",
"This page explains the customer information involved in shopping with ${brand}.":"This policy explains how customer information is used when you browse our store, place an order, or contact us for assistance.",
"${brand} offers a 60-day return window.":"We offer a 60-day return window.",
"When purchasing from ${brand}, review the product description, selected options, quantity, contact information, and delivery address before submitting the order.":"Before placing an order, review the product description, selected options, quantity, contact information, and delivery address.",
"Welcome to ${brand}. This website lets you browse our products, read information about the store, and place orders.":"These terms describe how to use our online store. You can browse products, review store information, and place orders through this website.",
"At {brand}, we encourage you to bring that perspective to the products you consider.":"Keep those preferences in mind as you explore the products available in our store.",
"We hope you approach {brand} with the same freedom to ask and compare that you would want in any considered purchase.":"You are welcome to ask questions and compare options before deciding what suits you.",
"At {brand}, we want the experience of finding value to include both the product and the practical terms of the purchase.":"For us, value includes both the usefulness of a product and a clear understanding of the purchase terms.",
"At {brand}, we appreciate the customers who browse with a clear purpose just as much as those who come to explore.":"Whether you arrive with a specific need or simply want to explore, we aim to make the information you need easy to find.",
"We want the tone of {brand} to support that kind of experience.":"Our aim is to offer a welcoming place to browse and make informed choices at your own pace.",
"At {brand}, we want the customer service pages to provide a starting point for those conversations, so that a question has somewhere to go instead of becoming a reason to feel uncertain about the next step.":"Our customer service pages provide a starting point for those conversations, with practical guidance on orders, delivery, and returns. If you still need help, use the contact information provided to explain your question.",
}
for old,new in changes.items():
    assert old in s,old
    s=s.replace(old,new)
# The separate marketing output can still use an optional brand supplied for SEO/prompts.
s=s.replace("const marketing={", "const brandLabel=(v.brand||'').trim(),fromBrand=brandLabel?` from ${brandLabel}`:'',seoBrand=brandLabel?` | ${brandLabel}`:'';\n  const marketing={")
s=s.replace('from ${v.brand}', '${fromBrand}'.lstrip())
# Remove the space before a conditional phrase so an omitted brand leaves natural punctuation.
s=s.replace('${product} ${fromBrand}', '${product}${fromBrand}')
s=s.replace('${term} | ${v.brand}', '${term}${seoBrand}')
assert '${brand}' not in s and '{brand}' not in s
p.write_text(s,encoding='utf8')
p=root/'dist/app.js';s=p.read_text(encoding='utf8').replace('请填写品牌名称、参考标题、参考内容和折扣额度。','请填写参考标题、参考内容和折扣额度。').replace("['brand','refTitle','refBody'].some", "['refTitle','refBody'].some").replace('品牌名称、参考标题和参考内容不能只包含空格。','参考标题和参考内容不能只包含空格。');p.write_text(s,encoding='utf8')
p=root/'dist/index.html';s=p.read_text(encoding='utf8').replace('<label>你的品牌名称<input id="brand" required','<label>品牌名称 <small>选填，仅用于 SEO 和提示词</small><input id="brand"').replace('generator.js?v=local1','generator.js?v=generic1').replace('app.js?v=prompt1','app.js?v=generic1').replace('prompt.js?v=sizehtml1','prompt.js?v=generic1');p.write_text(s,encoding='utf8')
p=root/'dist/prompt.js';s=p.read_text(encoding='utf8').replace('${values.brand}',"${values.brand||'未提供，请使用通用称呼，不要编造品牌名'}");p.write_text(s,encoding='utf8')
for file in ['README.md','package-portable.py']:
 p=root/file;s=p.read_text(encoding='utf8');s=s.replace('填写品牌名称、参考网站描述的标题和内容、最高折扣','填写参考网站描述的标题和内容、最高折扣（品牌名称选填，仅用于 SEO 和提示词）').replace('填写品牌名称、参考描述的标题和内容、最高折扣','填写参考描述的标题和内容、最高折扣（品牌名称选填，仅用于 SEO 和提示词）');p.write_text(s,encoding='utf8')
