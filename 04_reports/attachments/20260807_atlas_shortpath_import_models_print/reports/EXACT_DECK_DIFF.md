# Exact active-deck diff from the preceding import-only packet

```diff
--- PREFLIGHT_ATLAS_IMPORT_ONLY_GAN_ZNO_TRANSPORT_IDENTITY.in
+++ PREFLIGHT_ATLAS_SHORTPATH_IMPORT_MODELS_PRINT.in
@@
-go atlas simflags="-V 5.40.0.R -P 4"
-mesh infile="/root/DECKBUILD/preflight/VICTORYMESH_SEB_ATLAS_TRANSPORT_RESAVE_D75BFD9_20260807/VM_SEB_STAGE2_conformal_track_x10p25_atlas_transport_mapped.str"
-quit
+go atlas simflags="-V 5.40.0.R -P 4"
+mesh infile="/root/DECKBUILD/preflight/AI70/t.str"
+models print
+quit
```

Active statement counts in the executed packet:

```text
go atlas=1
mesh infile=1
models print=1
quit=1
solve=0
material/mobility/impact/interface/thermcontact/method/probe/output/save/load=0
singleeventupset/tfinal/system/ssh/shell=0
```
