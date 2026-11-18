# 垂直流超净工作台

这是为微形展厅制作的通用器械模型。顶部的预滤网、送风机组和主过滤盒位于工作腔上方。前窗、工作面、机架和顶罩分别建模。冷白色喷粉外壳、钴蓝机架、海军蓝饰条、玻璃和拉丝钢使用独立材质。

打开 `clean-bench.blend` 可编辑部件，在第 1 帧看整机，第 101 帧看拆解。渲染脚本会生成透明底的 `assembled.png` 和浅蓝灰棚拍的 `exploded.png`。[网页 GLB 模型](../../docs/assets/models/clean-bench.glb) 保留七个命名组，`parts.json` 给出网页位移和视角。比例、面板和拆解行程均为教学设计。

送风与过滤部件的相对位置参考设备厂商的纵向气流图。[Air Science 产品手册，第 5 页](https://www.airscience.com/lib/sitefiles/pdf/SalesLit/11470_7_AIR_Purair_LF_Brochure_vf1.pdf#page=5)

前窗、侧窗和控制面板的组成参考垂直流工作台的产品说明。模型几何和外观由本项目绘制。[Labconco 产品说明](https://www.labconco.com/product/purifier-vertical-clean-benches)

使用 Blender 5.3 与 `blender-cell-biology` skill 重建。外部安装的 skill 可通过 `CELL_BIOLOGY_SKILL` 指定。

```sh
blender -b --factory-startup --python-exit-code 1 -P build.py -- --out ./output --width 1920 --samples 84
```
