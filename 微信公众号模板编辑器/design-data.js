// ====== 微信公众号模板设计系统 ======
// 自动从 6001 个模板蒸馏的分类数据与设计规范

var DESIGN_SYSTEM = {
  total: 6001,
  colors: {"红色":1537,"蓝色":1563,"绿色":1267,"黄色":697,"粉色":289,"棕色":237,"橙色":260,"紫色":75,"灰色":118,"杏色":44,"咖色":27,"金色":38,"白色":3,"黑色":13,"彩色":20,"莫兰迪":79},
  industries: {"教育":1640,"校园":1649,"学校":314,"医疗":240,"健康":195,"疾病":35,"党政":298,"党建":131,"政务":329,"餐饮":43,"美食":40,"企业":657,"公司":113,"科技":198,"旅游":206,"旅行":137,"金融":36,"银行":20,"电商":101,"家居":15,"房产":2,"体育":79,"运动":108,"娱乐":18,"音乐":43,"节日":291,"节气":360,"幼儿园":422,"大学":214,"中学":47,"培训":107,"夏令营":67,"招生":92,"就业":11,"招聘":63,"安全":245,"环保":45,"公益":66,"能源":42,"电力":26,"石油":36,"燃气":20,"农业":12,"司法":10,"法律":21,"服装":9,"服饰":10,"物业":3},
  styles: {"简约":4116,"极简":180,"商务":871,"文艺":939,"清新":775,"卡通":577,"可爱":158,"手绘":283,"插画":372,"国风":367,"古风":244,"中国风":300,"水墨":24,"水彩":135,"撕纸":114,"拼贴":26,"杂志":230,"INS":70,"时尚":53,"潮流":17,"高级":220,"大气":109,"喜庆":268,"孟菲斯":11,"多巴胺":6,"渐变":53,"弥散":12,"实景":18,"3D":33,"复古":41,"美拉德":7,"个性":10,"浪漫":81,"温馨":34,"科技":198,"国潮":25,"剪纸":7},
  colorTokens: {"红色":{"primary":"#C62828","light":"#FFCDD2","dark":"#8E0000","bg":"#FFF5F5","accent":"#E53935","secondary":"#FF8A80"},"蓝色":{"primary":"#1565C0","light":"#BBDEFB","dark":"#0D47A1","bg":"#E3F2FD","accent":"#1E88E5","secondary":"#64B5F6"},"绿色":{"primary":"#2E7D32","light":"#C8E6C9","dark":"#1B5E20","bg":"#E8F5E9","accent":"#43A047","secondary":"#81C784"},"黄色":{"primary":"#F9A825","light":"#FFF9C4","dark":"#F57F17","bg":"#FFFDE7","accent":"#FFC107","secondary":"#FFD54F"},"粉色":{"primary":"#D81B60","light":"#F8BBD0","dark":"#880E4F","bg":"#FCE4EC","accent":"#E91E63","secondary":"#F48FB1"},"棕色":{"primary":"#5D4037","light":"#D7CCC8","dark":"#3E2723","bg":"#EFEBE9","accent":"#795548","secondary":"#A1887F"},"橙色":{"primary":"#E65100","light":"#FFE0B2","dark":"#BF360C","bg":"#FFF3E0","accent":"#FF6D00","secondary":"#FFAB40"},"紫色":{"primary":"#6A1B9A","light":"#E1BEE7","dark":"#4A148C","bg":"#F3E5F5","accent":"#8E24AA","secondary":"#CE93D8"},"灰色":{"primary":"#546E7A","light":"#CFD8DC","dark":"#37474F","bg":"#ECEFF1","accent":"#78909C","secondary":"#B0BEC5"},"杏色":{"primary":"#D4A574","light":"#F5E6D3","dark":"#A67B5B","bg":"#FDF5EE","accent":"#C49A6C","secondary":"#E8C9A0"},"咖色":{"primary":"#795548","light":"#BCAAA4","dark":"#4E342E","bg":"#EFEBE9","accent":"#8D6E63","secondary":"#A1887F"},"金色":{"primary":"#C8A951","light":"#F5E6B8","dark":"#9E7E2E","bg":"#FDF8E7","accent":"#D4AF37","secondary":"#E8C96A"},"莫兰迪":{"primary":"#9E9E9E","light":"#BDBDBD","dark":"#757575","bg":"#FAFAFA","accent":"#B0BEC5","secondary":"#CFD8DC"},"彩色":{"primary":"#FF5722","light":"#FFCCBC","dark":"#BF360C","bg":"#FBE9E7","accent":"#FF7043","secondary":"#FFAB91"}},
  industryColorMap: {"教育":[{"color":"蓝色","count":465},{"color":"绿色","count":424},{"color":"红色","count":317},{"color":"黄色","count":268},{"color":"橙色","count":76}],"校园":[{"color":"绿色","count":439},{"color":"蓝色","count":429},{"color":"红色","count":298},{"color":"黄色","count":249},{"color":"橙色","count":80}],"学校":[{"color":"蓝色","count":91},{"color":"绿色","count":77},{"color":"黄色","count":54},{"color":"红色","count":49},{"color":"橙色","count":16}],"医疗":[{"color":"蓝色","count":136},{"color":"绿色","count":47},{"color":"粉色","count":21},{"color":"红色","count":10},{"color":"紫色","count":8}],"健康":[{"color":"蓝色","count":83},{"color":"绿色","count":44},{"color":"粉色","count":20},{"color":"黄色","count":19},{"color":"橙色","count":10}],"疾病":[{"color":"蓝色","count":21},{"color":"绿色","count":6},{"color":"黄色","count":3},{"color":"橙色","count":2},{"color":"红色","count":1}],"党政":[{"color":"红色","count":263},{"color":"黄色","count":25},{"color":"蓝色","count":11},{"color":"灰色","count":8},{"color":"绿色","count":6}],"党建":[{"color":"红色","count":124},{"color":"黄色","count":4},{"color":"杏色","count":3},{"color":"绿色","count":1},{"color":"橙色","count":1}],"政务":[{"color":"红色","count":283},{"color":"蓝色","count":27},{"color":"黄色","count":17},{"color":"灰色","count":7},{"color":"绿色","count":6}],"餐饮":[{"color":"红色","count":12},{"color":"黄色","count":8},{"color":"棕色","count":7},{"color":"绿色","count":6},{"color":"蓝色","count":3}],"美食":[{"color":"黄色","count":12},{"color":"红色","count":8},{"color":"绿色","count":7},{"color":"棕色","count":6},{"color":"橙色","count":3}],"企业":[{"color":"红色","count":267},{"color":"蓝色","count":169},{"color":"绿色","count":83},{"color":"黄色","count":38},{"color":"橙色","count":27}],"公司":[{"color":"红色","count":56},{"color":"蓝色","count":35},{"color":"绿色","count":12},{"color":"橙色","count":4},{"color":"粉色","count":3}],"科技":[{"color":"蓝色","count":159},{"color":"红色","count":12},{"color":"紫色","count":11},{"color":"绿色","count":9},{"color":"橙色","count":4}],"旅游":[{"color":"绿色","count":92},{"color":"蓝色","count":54},{"color":"黄色","count":22},{"color":"灰色","count":11},{"color":"棕色","count":9}],"旅行":[{"color":"绿色","count":68},{"color":"蓝色","count":37},{"color":"黄色","count":16},{"color":"棕色","count":10},{"color":"粉色","count":8}],"金融":[{"color":"蓝色","count":14},{"color":"橙色","count":6},{"color":"金色","count":5},{"color":"红色","count":4},{"color":"黄色","count":3}],"银行":[{"color":"蓝色","count":8},{"color":"金色","count":5},{"color":"橙色","count":4},{"color":"红色","count":3},{"color":"黄色","count":1}],"电商":[{"color":"红色","count":44},{"color":"黄色","count":14},{"color":"粉色","count":12},{"color":"棕色","count":9},{"color":"绿色","count":8}],"家居":[{"color":"棕色","count":7},{"color":"绿色","count":2},{"color":"黄色","count":1},{"color":"灰色","count":1}],"房产":[{"color":"红色","count":1},{"color":"棕色","count":1}],"体育":[{"color":"蓝色","count":30},{"color":"绿色","count":26},{"color":"黄色","count":17},{"color":"橙色","count":8},{"color":"红色","count":3}],"运动":[{"color":"蓝色","count":37},{"color":"绿色","count":33},{"color":"黄色","count":21},{"color":"橙色","count":14},{"color":"红色","count":4}],"娱乐":[{"color":"蓝色","count":4},{"color":"粉色","count":4},{"color":"紫色","count":3},{"color":"棕色","count":2},{"color":"红色","count":1}],"音乐":[{"color":"蓝色","count":11},{"color":"紫色","count":10},{"color":"黄色","count":5},{"color":"粉色","count":5},{"color":"绿色","count":4}],"节日":[{"color":"红色","count":118},{"color":"黄色","count":45},{"color":"粉色","count":45},{"color":"蓝色","count":38},{"color":"绿色","count":35}],"节气":[{"color":"绿色","count":143},{"color":"蓝色","count":84},{"color":"黄色","count":59},{"color":"棕色","count":28},{"color":"橙色","count":17}],"幼儿园":[{"color":"黄色","count":107},{"color":"绿色","count":95},{"color":"蓝色","count":86},{"color":"红色","count":66},{"color":"粉色","count":31}],"大学":[{"color":"蓝色","count":81},{"color":"绿色","count":54},{"color":"红色","count":39},{"color":"黄色","count":14},{"color":"橙色","count":6}],"中学":[{"color":"蓝色","count":15},{"color":"红色","count":11},{"color":"绿色","count":11},{"color":"杏色","count":4},{"color":"黄色","count":2}],"培训":[{"color":"蓝色","count":46},{"color":"绿色","count":22},{"color":"红色","count":14},{"color":"黄色","count":11},{"color":"橙色","count":7}],"夏令营":[{"color":"绿色","count":34},{"color":"蓝色","count":26},{"color":"黄色","count":2},{"color":"棕色","count":2},{"color":"橙色","count":2}],"招生":[{"color":"蓝色","count":32},{"color":"绿色","count":21},{"color":"黄色","count":15},{"color":"红色","count":11},{"color":"橙色","count":6}],"就业":[{"color":"蓝色","count":6},{"color":"绿色","count":3},{"color":"紫色","count":1}],"招聘":[{"color":"蓝色","count":33},{"color":"绿色","count":15},{"color":"黄色","count":10},{"color":"橙色","count":4},{"color":"红色","count":1}],"安全":[{"color":"蓝色","count":104},{"color":"红色","count":72},{"color":"绿色","count":37},{"color":"黄色","count":31},{"color":"橙色","count":6}],"环保":[{"color":"绿色","count":28},{"color":"蓝色","count":18},{"color":"黄色","count":1}],"公益":[{"color":"红色","count":19},{"color":"蓝色","count":18},{"color":"绿色","count":11},{"color":"黄色","count":9},{"color":"粉色","count":4}],"能源":[{"color":"蓝色","count":25},{"color":"绿色","count":10},{"color":"红色","count":5},{"color":"灰色","count":2},{"color":"橙色","count":1}],"电力":[{"color":"蓝色","count":9},{"color":"绿色","count":7},{"color":"橙色","count":5},{"color":"黄色","count":3},{"color":"红色","count":2}],"石油":[{"color":"蓝色","count":11},{"color":"橙色","count":9},{"color":"绿色","count":8},{"color":"黄色","count":7},{"color":"红色","count":4}],"燃气":[{"color":"蓝色","count":7},{"color":"绿色","count":6},{"color":"红色","count":4}],"农业":[{"color":"绿色","count":7},{"color":"黄色","count":3},{"color":"红色","count":1},{"color":"橙色","count":1}],"司法":[{"color":"棕色","count":6},{"color":"蓝色","count":5},{"color":"灰色","count":2},{"color":"黄色","count":1}],"法律":[{"color":"蓝色","count":11},{"color":"棕色","count":6},{"color":"红色","count":5},{"color":"黄色","count":3},{"color":"灰色","count":2}],"服装":[{"color":"棕色","count":7},{"color":"橙色","count":1}],"服饰":[{"color":"棕色","count":8},{"color":"红色","count":1},{"color":"黄色","count":1},{"color":"橙色","count":1}],"物业":[{"color":"红色","count":1},{"color":"黄色","count":1},{"color":"杏色","count":1}]},
  industryStyleMap: {"教育":[{"style":"简约","count":1144},{"style":"文艺","count":323},{"style":"卡通","count":299},{"style":"清新","count":285},{"style":"商务","count":139}],"校园":[{"style":"简约","count":1083},{"style":"文艺","count":395},{"style":"清新","count":309},{"style":"卡通","count":307},{"style":"手绘","count":129}],"学校":[{"style":"简约","count":199},{"style":"清新","count":82},{"style":"卡通","count":74},{"style":"文艺","count":52},{"style":"可爱","count":31}],"医疗":[{"style":"简约","count":207},{"style":"商务","count":39},{"style":"插画","count":21},{"style":"卡通","count":18},{"style":"高级","count":11}],"健康":[{"style":"简约","count":125},{"style":"插画","count":39},{"style":"卡通","count":30},{"style":"国风","count":15},{"style":"中国风","count":15}],"疾病":[{"style":"简约","count":33},{"style":"商务","count":9},{"style":"卡通","count":2},{"style":"插画","count":2},{"style":"文艺","count":1}],"党政":[{"style":"简约","count":248},{"style":"商务","count":40},{"style":"喜庆","count":22},{"style":"大气","count":18},{"style":"插画","count":13}],"党建":[{"style":"简约","count":124},{"style":"商务","count":23},{"style":"大气","count":10},{"style":"国风","count":4},{"style":"中国风","count":4}],"政务":[{"style":"简约","count":308},{"style":"商务","count":51},{"style":"高级","count":15},{"style":"大气","count":14},{"style":"极简","count":4}],"餐饮":[{"style":"简约","count":30},{"style":"高级","count":15},{"style":"手绘","count":7},{"style":"商务","count":3},{"style":"文艺","count":3}],"美食":[{"style":"简约","count":23},{"style":"高级","count":12},{"style":"手绘","count":7},{"style":"卡通","count":4},{"style":"插画","count":4}],"企业":[{"style":"简约","count":470},{"style":"商务","count":193},{"style":"科技","count":73},{"style":"极简","count":72},{"style":"杂志","count":72}],"公司":[{"style":"简约","count":99},{"style":"商务","count":47},{"style":"高级","count":16},{"style":"大气","count":13},{"style":"科技","count":13}],"科技":[{"style":"科技","count":198},{"style":"简约","count":176},{"style":"商务","count":141},{"style":"渐变","count":9},{"style":"高级","count":6}],"旅游":[{"style":"简约","count":105},{"style":"杂志","count":64},{"style":"文艺","count":59},{"style":"极简","count":58},{"style":"清新","count":36}],"旅行":[{"style":"简约","count":81},{"style":"文艺","count":40},{"style":"清新","count":33},{"style":"杂志","count":20},{"style":"撕纸","count":17}],"金融":[{"style":"简约","count":36},{"style":"商务","count":26},{"style":"科技","count":2},{"style":"渐变","count":1}],"银行":[{"style":"简约","count":20},{"style":"商务","count":15},{"style":"科技","count":1}],"电商":[{"style":"简约","count":59},{"style":"文艺","count":16},{"style":"时尚","count":13},{"style":"杂志","count":11},{"style":"清新","count":10}],"家居":[{"style":"极简","count":13},{"style":"杂志","count":11},{"style":"简约","count":7},{"style":"INS","count":6},{"style":"高级","count":5}],"房产":[{"style":"简约","count":2},{"style":"高级","count":1}],"体育":[{"style":"简约","count":69},{"style":"卡通","count":9},{"style":"高级","count":6},{"style":"手绘","count":5},{"style":"清新","count":4}],"运动":[{"style":"简约","count":90},{"style":"卡通","count":14},{"style":"清新","count":9},{"style":"高级","count":8},{"style":"手绘","count":7}],"娱乐":[{"style":"简约","count":10},{"style":"撕纸","count":5},{"style":"时尚","count":4},{"style":"卡通","count":3},{"style":"手绘","count":2}],"音乐":[{"style":"简约","count":18},{"style":"文艺","count":10},{"style":"清新","count":10},{"style":"时尚","count":7},{"style":"潮流","count":6}],"节日":[{"style":"简约","count":153},{"style":"国风","count":52},{"style":"插画","count":44},{"style":"中国风","count":43},{"style":"古风","count":38}],"节气":[{"style":"简约","count":112},{"style":"国风","count":105},{"style":"插画","count":92},{"style":"清新","count":82},{"style":"中国风","count":82}],"幼儿园":[{"style":"简约","count":186},{"style":"卡通","count":182},{"style":"清新","count":111},{"style":"文艺","count":92},{"style":"可爱","count":75}],"大学":[{"style":"简约","count":188},{"style":"商务","count":77},{"style":"清新","count":9},{"style":"插画","count":9},{"style":"撕纸","count":8}],"中学":[{"style":"简约","count":42},{"style":"商务","count":5},{"style":"清新","count":4},{"style":"卡通","count":4},{"style":"喜庆","count":2}],"培训":[{"style":"简约","count":85},{"style":"文艺","count":22},{"style":"商务","count":17},{"style":"卡通","count":17},{"style":"清新","count":15}],"夏令营":[{"style":"简约","count":43},{"style":"卡通","count":13},{"style":"文艺","count":9},{"style":"撕纸","count":8},{"style":"清新","count":6}],"招生":[{"style":"简约","count":66},{"style":"卡通","count":24},{"style":"清新","count":11},{"style":"商务","count":9},{"style":"文艺","count":6}],"就业":[{"style":"简约","count":10},{"style":"商务","count":5},{"style":"时尚","count":1},{"style":"潮流","count":1}],"招聘":[{"style":"简约","count":49},{"style":"商务","count":26},{"style":"清新","count":5},{"style":"卡通","count":5},{"style":"科技","count":5}],"安全":[{"style":"简约","count":169},{"style":"卡通","count":57},{"style":"商务","count":34},{"style":"插画","count":19},{"style":"清新","count":15}],"环保":[{"style":"简约","count":26},{"style":"插画","count":12},{"style":"清新","count":10},{"style":"卡通","count":8},{"style":"手绘","count":5}],"公益":[{"style":"简约","count":45},{"style":"插画","count":11},{"style":"卡通","count":8},{"style":"商务","count":5},{"style":"文艺","count":5}],"能源":[{"style":"简约","count":41},{"style":"商务","count":26},{"style":"科技","count":3}],"电力":[{"style":"简约","count":26},{"style":"商务","count":13},{"style":"高级","count":12},{"style":"极简","count":1},{"style":"科技","count":1}],"石油":[{"style":"简约","count":36},{"style":"商务","count":5},{"style":"极简","count":1}],"燃气":[{"style":"简约","count":20},{"style":"商务","count":20}],"农业":[{"style":"简约","count":9},{"style":"商务","count":7},{"style":"手绘","count":3},{"style":"科技","count":3},{"style":"卡通","count":2}],"司法":[{"style":"简约","count":10},{"style":"商务","count":10}],"法律":[{"style":"简约","count":17},{"style":"商务","count":11},{"style":"卡通","count":1},{"style":"插画","count":1}],"服装":[{"style":"简约","count":4},{"style":"撕纸","count":4},{"style":"时尚","count":4},{"style":"文艺","count":3},{"style":"复古","count":3}],"服饰":[{"style":"简约","count":5},{"style":"时尚","count":5},{"style":"极简","count":3},{"style":"文艺","count":3},{"style":"撕纸","count":2}],"物业":[{"style":"简约","count":3},{"style":"大气","count":1}]},
  industryNormalizer: {
    "教育":"教育","校园":"教育","学校":"教育","幼儿园":"教育","大学":"教育","中学":"教育","培训":"教育培训",
    "医疗":"医疗健康","健康":"医疗健康","疾病":"医疗健康",
    "党政":"党政政务","党建":"党政政务","政务":"党政政务",
    "餐饮":"餐饮美食","美食":"餐饮美食",
    "企业":"企业公司","公司":"企业公司","科技":"科技互联网",
    "旅游":"旅游出行","旅行":"旅游出行",
    "金融":"金融银行","银行":"金融银行",
    "电商":"电商促销","家居":"生活家居","房产":"生活家居",
    "体育":"体育运动","运动":"体育运动",
    "娱乐":"影视娱乐","音乐":"影视娱乐",
    "节日":"节日节气","节气":"节日节气",
    "安全":"安全科普","环保":"公益环保","公益":"公益环保",
    "能源":"能源电力","电力":"能源电力","石油":"能源石油","燃气":"能源燃气",
    "农业":"农林牧渔","司法":"司法法律","法律":"司法法律",
    "服装":"服饰穿搭","服饰":"服饰穿搭"
  },

  // 行业关键词→标准名称
  getIndustryName: function(keywords) {
    for (var i = 0; i < keywords.length; i++) {
      var kw = keywords[i];
      if (this.industryNormalizer[kw]) return this.industryNormalizer[kw];
    }
    return null;
  },

  // 根据关键词推荐配色+风格
  recommendDesign: function(keywords) {
    var rec = { colors: [], styles: [] };
    var colorScores = {};
    var styleScores = {};
    for (var i = 0; i < keywords.length; i++) {
      var kw = keywords[i];
      if (this.industryColorMap[kw]) {
        var cdata = this.industryColorMap[kw];
        for (var j = 0; j < cdata.length; j++) {
          var item = cdata[j];
          if (!colorScores[item.color]) colorScores[item.color] = 0;
          colorScores[item.color] += item.count;
        }
      }
      if (this.industryStyleMap[kw]) {
        var sdata = this.industryStyleMap[kw];
        for (var j = 0; j < sdata.length; j++) {
          var item = sdata[j];
          if (!styleScores[item.style]) styleScores[item.style] = 0;
          styleScores[item.style] += item.count;
        }
      }
    }
    // Sort
    var colorArr = Object.keys(colorScores).map(function(k) { return {color:k, count:colorScores[k]}; });
    colorArr.sort(function(a,b) { return b.count - a.count; });
    rec.colors = colorArr.slice(0,5).map(function(x) { return x.color; });
    var styleArr = Object.keys(styleScores).map(function(k) { return {style:k, count:styleScores[k]}; });
    styleArr.sort(function(a,b) { return b.count - a.count; });
    rec.styles = styleArr.slice(0,5).map(function(x) { return x.style; });
    return rec;
  }
};

var DESIGN_RULES = {
  // 排版规范（从模板统计蒸馏）
  typography: {
    baseSize: "15px",
    smallSize: "13px",
    h1Size: "22px",
    h2Size: "19px",
    h3Size: "17px",
    lineHeight: "1.8",
    color: "#333333",
    secondaryColor: "#666666",
    fontFamily: "-apple-system, PingFang SC, Microsoft YaHei"
  },
  spacing: {
    sectionGap: "12px",
    padding: "15px",
    contentWidth: "420px"
  },
  borderRadius: "6px",

  // 布局模式库
  layoutPatterns: [
    { id:"standard", name:"标准图文", desc:"标题+正文+图片+结尾", usage:"通用" },
    { id:"magazine", name:"杂志风格", desc:"大图+标题+摘录+留白", usage:"旅游/文艺/品牌" },
    { id:"card", name:"卡片布局", desc:"多卡片并列，图文分离", usage:"活动/产品/招聘" },
    { id:"poster", name:"海报风格", desc:"全屏背景+居中标题+CTA", usage:"节日/活动/促销" },
    { id:"minimal", name:"极简留白", desc:"大量留白+细线条+小字", usage:"高端/艺术/散文" },
    { id:"timeline", name:"时间线", desc:"纵向时间轴+节点", usage:"历程/会议/活动序列" },
    { id:"split", name:"左右分栏", desc:"图左文右或文左图右", usage:"人物/产品对比" },
    { id:"banner", name:"横幅大图", desc:"通栏大图+覆盖文字", usage:"活动宣传/节日祝福" }
  ],

  // 组件样式
  titleStyles: {
    solid: { name:"纯色背景标题", desc:"背景色+白色文字+圆角" },
    leftBar: { name:"左侧竖条标题", desc:"左边框装饰+无背景" },
    underline: { name:"下划线标题", desc:"底部边框装饰" },
    icon: { name:"图标标题", desc:"小图标+文字" },
    center: { name:"居中大标题", desc:"大字号+居中+底部装饰" }
  },
  dividerStyles: {
    solid: { name:"实线分割" },
    dashed: { name:"虚线分割" },
    gradient: { name:"渐变分割" },
    icon: { name:"图标分割" }
  }
};