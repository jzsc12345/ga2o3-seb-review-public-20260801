# RUN096 → RUN118 全量 deck diff

本文件由 `scripts\run118_contract_check.py --diff-output` 机械生成；没有省略差异行。

```diff
--- decks\RUN096_Wang2026_nofp_Lgd9_x11_hfo2hc_SEB_1000V_Et0p8_long.in
+++ decks\RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_short500ns.in
@@ -1,18 +1,20 @@
 # =============================================================================
-# RUN096 -- HfO2 heat-capacity-only arm from completed RUN095
+# RUN118 -- 500 ns high-field electron VSAT(T) OFAT from frozen RUN096
 #
 # Goal:
-#   Quantify only the missing HfO2 heat-capacity model after RUN095 closed the
-#   HEAT.FULL root-cause branch. Geometry, electrical physics, source, thermal
-#   boundaries, heat-source equation and time schedule are frozen from RUN095.
+#   Replace only the constant electron VSATN in regions 3-7 with the minimal
+#   ATLAS SCI F.VSATN(T) callback validated by RUN117. Geometry, mesh, doping,
+#   Fe, impact, source, thermal physics/boundaries, solver and every time step
+#   through 500 ns are frozen from RUN096. Stop after the 500 ns snapshot.
 #   Integrate PHOTOGEN and require the generated charge to agree with
 #   0.4529 pC/um * 5.35 um = 2.423015 pC within 5 percent.
 #
-# Contract relative to RUN092:
-#   The only physical change is lateral geometry: xdev 31->20 um,
-#   drain-left 29->18 um (Lgd 20->9 um), and removal of gate_fp.  The 5 um
-#   substrate, Fe trap, channel/UID, work functions, mobility, impact,
-#   thermal parameters/contacts, source, solver and time schedule are frozen.
+# Contract relative to RUN096:
+#   The only physical change is electron high-field VSATN:
+#   constant 2.0e7 cm/s -> RUN117-validated F.VSATN(T), anchored to the same
+#   2.0e7 cm/s at 300 K. VSATP, BETAN/BETAP and all low-field mobility stay
+#   unchanged. Removing the 1 us-100 us execution tail is non-physical I/O and
+#   scheduling truncation after the last state used by this experiment.
 #
 # Structure/contact lineage:
 #   RUN021: no-FP means source/drain/gate zero-area contacts only.
@@ -173,13 +175,13 @@
             max.height=$ion_dy_sub max.width=$ion_dx
 
 mesh mode=MeshBuild
-structure outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_mesh.str"
+structure outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_mesh.str"
 
 # -----------------------------------------------------------------------------
 # Stage 2: frozen RUN047 equations with a low-field transfer sweep
 # -----------------------------------------------------------------------------
 go atlas simflags="-V 5.40.0.R -P 4"
-mesh infile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_mesh.str"
+mesh infile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_mesh.str"
 
 doping gauss n.type conc=$nd_sd char=1.0 lat.char=1.0 \
        x.min=$x_drn_l y.min=$y_surface y.max=$y_channel_b
@@ -191,7 +193,8 @@
          edb=0.06 gcb=2.0 eab=1.0 gvb=4.0 \
          augn=2.8e-31 augp=9.9e-32 \
          tcon.const tc.const=$kappa_g \
-         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0
+         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0 \
+         f.vsatn="/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns/RUN118_ga2o3_vsatn.lib"
 material region=4 user.group=semiconductor user.default=GaN \
          affinity=$chi_g eg300=$eg_g egalph=0 egbeta=0 \
          permittivity=$eps_g nc300=$nc_g nv300=$nv_g \
@@ -199,7 +202,8 @@
          edb=0.06 gcb=2.0 eab=1.0 gvb=4.0 \
          augn=2.8e-31 augp=9.9e-32 \
          tcon.const tc.const=$kappa_g \
-         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0
+         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0 \
+         f.vsatn="/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns/RUN118_ga2o3_vsatn.lib"
 material region=5 user.group=semiconductor user.default=GaN \
          affinity=$chi_g eg300=$eg_g egalph=0 egbeta=0 \
          permittivity=$eps_g nc300=$nc_g nv300=$nv_g \
@@ -207,7 +211,8 @@
          edb=0.06 gcb=2.0 eab=1.0 gvb=4.0 \
          augn=2.8e-31 augp=9.9e-32 \
          tcon.const tc.const=$kappa_g \
-         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0
+         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0 \
+         f.vsatn="/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns/RUN118_ga2o3_vsatn.lib"
 material region=6 user.group=semiconductor user.default=GaN \
          affinity=$chi_g eg300=$eg_g egalph=0 egbeta=0 \
          permittivity=$eps_g nc300=$nc_g nv300=$nv_g \
@@ -215,7 +220,8 @@
          edb=0.06 gcb=2.0 eab=1.0 gvb=4.0 \
          augn=2.8e-31 augp=9.9e-32 \
          tcon.const tc.const=$kappa_g \
-         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0
+         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0 \
+         f.vsatn="/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns/RUN118_ga2o3_vsatn.lib"
 material region=7 user.group=semiconductor user.default=GaN \
          affinity=$chi_g eg300=$eg_g egalph=0 egbeta=0 \
          permittivity=$eps_g nc300=$nc_g nv300=$nv_g \
@@ -223,7 +229,8 @@
          edb=0.06 gcb=2.0 eab=1.0 gvb=4.0 \
          augn=2.8e-31 augp=9.9e-32 \
          tcon.const tc.const=$kappa_g \
-         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0
+         hc.std hc.a=$heatcap_g hc.b=0 hc.c=0 hc.d=0 \
+         f.vsatn="/root/DECKBUILD/runs/RUN118_wang1000-fvsatt-short500ns/RUN118_ga2o3_vsatn.lib"
 
 material region=1 permittivity=3.9 \
          tcon.const tc.const=0.014
@@ -237,35 +244,35 @@
          mu1p.caug=1e-6 mu2p.caug=$mup_g \
          ncritp.caug=1e17 deltap.caug=1.0 \
          alphap.caug=0 betap.caug=0 gammap.caug=0 \
-         vsatn=2.0e7 vsatp=2.0e7 betan=7.52 betap=7.52
+         vsatp=2.0e7 betan=7.52 betap=7.52
 mobility region=4 mu1n.caug=10 mu2n.caug=$mun_g \
          ncritn.caug=2e17 deltan.caug=1.0 \
          alphan.caug=0 betan.caug=0 gamman.caug=0 \
          mu1p.caug=1e-6 mu2p.caug=$mup_g \
          ncritp.caug=1e17 deltap.caug=1.0 \
          alphap.caug=0 betap.caug=0 gammap.caug=0 \
-         vsatn=2.0e7 vsatp=2.0e7 betan=7.52 betap=7.52
+         vsatp=2.0e7 betan=7.52 betap=7.52
 mobility region=5 mu1n.caug=10 mu2n.caug=$mun_g \
          ncritn.caug=2e17 deltan.caug=1.0 \
          alphan.caug=0 betan.caug=0 gamman.caug=0 \
          mu1p.caug=1e-6 mu2p.caug=$mup_g \
          ncritp.caug=1e17 deltap.caug=1.0 \
          alphap.caug=0 betap.caug=0 gammap.caug=0 \
-         vsatn=2.0e7 vsatp=2.0e7 betan=7.52 betap=7.52
+         vsatp=2.0e7 betan=7.52 betap=7.52
 mobility region=6 mu1n.caug=10 mu2n.caug=$mun_g \
          ncritn.caug=2e17 deltan.caug=1.0 \
          alphan.caug=0 betan.caug=0 gamman.caug=0 \
          mu1p.caug=1e-6 mu2p.caug=$mup_g \
          ncritp.caug=1e17 deltap.caug=1.0 \
          alphap.caug=0 betap.caug=0 gammap.caug=0 \
-         vsatn=2.0e7 vsatp=2.0e7 betan=7.52 betap=7.52
+         vsatp=2.0e7 betan=7.52 betap=7.52
 mobility region=7 mu1n.caug=10 mu2n.caug=$mun_g \
          ncritn.caug=2e17 deltan.caug=1.0 \
          alphan.caug=0 betan.caug=0 gamman.caug=0 \
          mu1p.caug=1e-6 mu2p.caug=$mup_g \
          ncritp.caug=1e17 deltap.caug=1.0 \
          alphap.caug=0 betap.caug=0 gammap.caug=0 \
-         vsatn=2.0e7 vsatp=2.0e7 betan=7.52 betap=7.52
+         vsatp=2.0e7 betan=7.52 betap=7.52
 
 impact region=3 selb an1=2.16e6 an2=2.16e6 bn1=1.77e7 bn2=1.77e7 \
        ap1=2.16e6 ap2=2.16e6 bp1=1.77e7 bp2=1.77e7 \
@@ -312,12 +319,12 @@
 
 solve init
 solve vgate=0 name=gate
-log outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_static.log"
+log outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_static.log"
 solve vdrain=0.1 name=drain
 solve name=drain vstep=0.5 vfinal=10 previous
 solve name=drain vstep=5.0 vfinal=$target_vds previous \
       compliance=1.6e-5 cname=drain
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_isothermal.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_isothermal.str"
 log off
 
 # Turn on the complete thermal equation in the same ATLAS process, preserving
@@ -333,7 +340,7 @@
 method block newton trap maxtraps=10 climit=1e-4 itlimit=50 max.temp=5000
 
 solve previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_prestrike.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_prestrike.str"
 
 singleeventupset entrypoint="$xion,$y_surface" exitpoint="$xion,$y_sub_b" \
                  radialgauss b.density=$qline pcunits radius=$ion_radius \
@@ -341,64 +348,53 @@
 probe integrated photogen name="GSEU_all" \
       x.min=0 x.max=$x_dev y.min=$y_sio2_top y.max=$y_sub_b
 
-log outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_transient.log"
+log outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_transient.log"
 solve tstop=2e-12 dt=2e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t2ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t2ps.str"
 solve tstop=6e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t6ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t6ps.str"
 solve tstop=9.8e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t9p8ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t9p8ps.str"
 solve tstop=14e-12 dt=1e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t14ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t14ps.str"
 solve tstop=20e-12 dt=2e-13 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t20ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t20ps.str"
 
 # Long recovery window. The sequence through 1 us is inherited from the
 # previously verified RUN038 long-tail schedule; 10/100 us extend it to
 # the Wang-paper recovery horizon without changing the source or physics.
 solve tstop=30e-12 dt=1e-12 previous
 solve tstop=50e-12 dt=1e-12 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t50ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t50ps.str"
 solve tstop=100e-12 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t100ps.str"
 solve tstop=400e-12 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t400ps.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t400ps.str"
 solve tstop=1e-9 dt=1e-11 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t1ns.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t1ns.str"
 solve tstop=2e-9 dt=1e-9 previous
 solve tstop=3e-9 dt=1e-9 previous
 solve tstop=4e-9 dt=1e-9 previous
 solve tstop=7e-9 dt=1e-9 previous
 solve tstop=9e-9 dt=1e-9 previous
 solve tstop=10e-9 dt=1e-9 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t10ns.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t10ns.str"
 solve tstop=20e-9 dt=1e-8 previous
 solve tstop=30e-9 dt=1e-8 previous
 solve tstop=40e-9 dt=1e-8 previous
 solve tstop=50e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t50ns.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t50ns.str"
 solve tstop=100e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100ns.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t100ns.str"
 solve tstop=500e-9 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t500ns.str"
-solve tstop=1e-6 dt=1e-8 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t1us.str"
-solve tstop=2e-6 dt=1e-7 previous
-solve tstop=5e-6 dt=2e-7 previous
-solve tstop=10e-6 dt=5e-7 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t10us.str"
-solve tstop=20e-6 dt=1e-6 previous
-solve tstop=50e-6 dt=2e-6 previous
-solve tstop=100e-6 dt=5e-6 previous
-save outfile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_t100us.str"
+save outfile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_t500ns.str"
 log off
 
-extract init infile="RUN096_Wang2026_nofp_Lgd9_x11_fulltrack_SEB_1000V_Et0p8_transient.log"
+extract init infile="RUN118_Wang2026_nofp_Lgd9_x11_fvsatT_SEB_1000V_Et0p8_transient.log"
 # 2-D area integral has units cm^-1; multiply by 1e-4 cm for a 1 um width.
-extract name="AreaTimeInt_cmInv_RUN096" area from curve(time, probe."GSEU_all")
+extract name="AreaTimeInt_cmInv_RUN118" area from curve(time, probe."GSEU_all")
 
 quit
 
 
 
-
```
