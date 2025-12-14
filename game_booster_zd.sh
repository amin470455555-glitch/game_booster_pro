#!/bin/bash
clear

# طرح اسم خودم 
# گرادیان سبز → لیمویی برای هدر ONLINE
green1='\e[38;5;40m'
green2='\e[38;5;82m'
green3='\e[38;5;118m'
reset='\e[0m'

# گرادیان صورتی → بنفش → آبی برای متن اصلی
pink='\e[38;5;198m'
purple='\e[38;5;129m'
blue='\e[38;5;63m'

# گرادیان آبی → سبز برای TERMUX
blue2='\e[38;5;39m'
green4='\e[38;5;48m'


# ─────────────────────────── هدر ONLINE ───────────────────────────
echo -e "${green1}<${green2}──────────────────────────────────────────────────${green3}>${reset}"
echo -e "                  ${green2}[★] O N L I N E [★]${reset}"
echo -e "${green1}<${green2}──────────────────────────────────────────────────${green3}>${reset}"
echo


# ─────────────────────────── متن وسط (گرادیان واقعی) ───────────────────────────
echo -e "              ${pink}__  ___                           _${reset}"
echo -e "             ${pink}/  |/  /____      ____ _____ ___  ${purple}(_)___${reset}"
echo -e "            ${pink}/ /|_/ / ___/_____/ __ \`/ __ \`__ \\/${purple} / __ \\${reset}"
echo -e "           ${purple}/ /  / / /  /_____/ /_/ / / / / / /${blue} / / / /${reset}"
echo -e "          ${blue}/_/  /_/_/         \\__,_/_/ /_/ /_/_/${blue}_/_/ /_/${reset}"
echo


# ─────────────────────────── فوتر TERMUX ───────────────────────────
echo -e "        ${blue2}<${green4}──────────────────────────────────────────────────${blue2}>${reset}"
echo -e "                  ${blue2}[★] T E R M U X [★]${reset}"
echo -e "        ${blue2}<${green4}──────────────────────────────────────────────────${blue2}>${reset}"


echo -e "\e[94m"
echo -e "\e[31m
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
██████╗░██╗░░░██╗██████╗░░██████╗░  ███████╗
██╔══██╗██║░░░██║██╔══██╗██╔════╝░  ██╔════╝
██████╦╝██║░░░██║██████╔╝██║░░██╗░  ██████╗░
██╔══██╗██║░░░██║██╔══██╗██║░░╚██╗  ╚════██╗
██████╦╝╚██████╔╝██║░░██║╚██████╔╝  ██████╔╝ PUBG BOOSTER
╚═════╝░░╚═════╝░╚═╝░░╚═╝░╚═════╝░  ╚═════╝░ PERFORMANCE
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
echo -e "\e[31m" "
  GAMING BOOSTER [ NON ROOT ]"
echo "╚══════════════════════════════════╝"
echo
echo -e "\e[94m"
message="◖ DEVICE AND HARDWARE INFO ◗"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
sleep 1

# نمایش اطلاعات دستگاه
message="➤ DEVICE $(getprop ro.product.brand)"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
sleep 1

message="➤ MODEL $(getprop ro.product.model)"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
sleep 1

message="➤ DEVELOPER: MR AMIN"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
sleep 1.s

message="➤ TELEGRAM: @MAYKI_1_SHOP_PUBG"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
sleep 1

message="➤ DEVELOPER ID: @mr_amin_vip"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
sleep 1

echo
echo -e "\e[31m"
message="  [  SELECT  GAME BOOSTER  ]"
for (( i=0; i<${#message}; i++ )); do
    echo -n "${message:$i:1}"
    sleep 0.1
done
echo
echo "╚═════════════════════════════╝"
sleep 2

# سوالات انتخاب
echo -e "\e[92m" "➤ Please select the game you want to optimize for:"
sleep 1.s

echo -e "\e[94m" "[ 1 ] PUBG"
sleep 0.5
echo -e "\e[94m" "[ 2 ] Call of Duty Mobile"
sleep 0.5
echo -n -e "\e[0m" "➤ ENTER NUMBER  = "
read game_choice

# عملیات بعد از انتخاب گیم
if [ "$game_choice" -eq 1 ]; then
    echo -e "\e[92m" "You selected PUBG Mobile!"
elif [ "$game_choice" -eq 2 ]; then
    echo -e "\e[92m" "You selected Call of Duty Mobile!"
else
    echo -e "\e[91m" "Invalid choice! Please restart the script."
    exit 1
fi

# اعمال تغییرات خاص بر اساس انتخاب گیم
echo -e "\e[94m" "◖ APPLYING BOOSTER FOR SELECTED GAME ◗"
echo -e "\e[94m"  "◖ DEVICE AND HARDWARE INFO ◗"
echo
echo "➤ DEVICE $(getprop ro.product.brand)"
sleep 0.5s
echo "➤ MODEL $(getprop ro.product.model)"
sleep 1s
echo
echo
echo -e "\e[31m" "
     [  SELECT  GAME BOOSTER  ]"
echo "╚═════════════════════════════╝"
echo
echo -e "\e[92m"" [ ** ] OPTIMIZE ANDROID ◗"
echo
echo -e "\e[94m"" [ 1 ] YES"
echo
echo -e "\e[94m"" [ 2 ] NO"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] SELECT FRAME RATE ◗"
echo
echo -e "\e[94m"" [ 1 ] 90FPS [ STABLE ]"
echo
echo -e "\e[94m"" [ 2 ] 60FPS [ STABLE ]"
echo
echo -e "\e[94m"" [ 3 ] 120FPS [ MAY NOT WORK ALL PHONE ]"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] SELECT REFRESH RATE ◗"
echo
echo -e "\e[94m"" [ 1 ] 90Hz [ STABLE ]"
echo
echo -e "\e[94m"" [ 2 ] 60Hz [ STABLE ]"
echo
echo -e "\e[94m"" [ 3 ] 120Hz [ MAY NOT WORK ALL PHONES ]"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] BOOST CPU LEVEL ◗"
echo
echo -e "\e[94m"" [ 1 ] HIGH  "
echo
echo -e "\e[94m"" [ 2 ] MEDIUM"
echo
echo -e "\e[94m"" [ 3 ] EXTREME [ DEVICE MAY HEAT ]"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] BOOST GPU LEVEL ◗"
echo
echo -e "\e[94m"" [ 1 ] HIGH "
echo
echo -e "\e[94m"" [ 2 ] MEDIUM"
echo
echo -e "\e[94m"" [ 3 ] EXTREME [ DEVICE MAY HEAT ]"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] RENDERING LAYER ◗"
echo
echo -e "\e[94m"" [ 1 ] VULKAN "
echo
echo -e "\e[94m"" [ 2 ] OPEN GL"
echo
echo -e "\e[94m"" [ 3 ] SKIA GL]"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] SELECT DEVICE MODE ◗"
echo
echo -e "\e[94m"" [ 1 ] BATTERY "
echo
echo -e "\e[94m"" [ 2 ] BALANCE"
echo
echo -e "\e[94m"" [ 3 ] PERFORMANCE"
echo
echo -e "\e[94m"" [ 4 ] GAMING "
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] SELECT TOUCH LEVEL  ◗"
echo
echo -e "\e[94m"" [ 1 ] HIGH "
echo
echo -e "\e[94m"" [ 2 ] LOW"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo -e "\e[92m"" [ ** ] BOOST NETWORK SPEED ◗"
echo
echo -e "\e[94m"" [ 1 ] YES "
echo
echo -e "\e[94m"" [ 2 ] NO"
echo
echo -n -e "\e[0m""➤ ENTER NUMBER  = "
read ram
sleep 1
echo
echo
Apply_Script() {
persist.sys.dalvik.hyperthreading=true
persist.sys.dalvik.multithread=true
[
name:gpu
cooling_name:MTK-cl-gpu
def_target:0
select_higher:1
]
[
name:battery
cooling_name:battery
def_target:0
select_higher:1
]
[
name:MTK-cl-backlight
cooling_name:MTK-cl-backlight
def_target:2047
select_higher:0
]
[
name:temp_state
path:/sys/class/thermal/thermal_message/temp_state
def_target:0
select_higher:1
]
[
name:chg_limit
path:/sys/class/power_supply/battery/reverse_limit
def_target:0
select_higher:1
]
[
name:cpu
path:/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
def_target:schedutil
select_higher:1
]
[
name:cpu
path:/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
def_target:interactive
select_higher:1
]
[
name:cpu0
path:/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq
def_target:2208000
select_higher:1
]
}
Apply_Script() {
Qualcomm
Adreno 660
OpenGL ES 3.2 V@0522.0 GIT@7c0af96f79, If3d5d77d59, 1608617347 Date:12/21/20
GL_OES_compressed_ETC1_RGB8_texture GL_AMD_compressed_ATC_texture GL_AMD_program_binary
GL_FILE props/op8t
GL_FILE cpuinfos/snap888
GL_FILE cpus/8cpu
GL_FILE ram/12gb
}
Apply_Script() {
settings put global activity_starts_logging_enabled 0
settings put global block_untrusted_touches 0
settings put global shadow_animation_scale 0
settings put system lockscreen_show_fingerprint_animation 0
settings put global adaptive_battery_management_enabled 0
settings put global ble_scan_always_enabled 0
settings put global app_standby_enabled 1
settings put global hardware_accelerated_rendering_enabled 1
settings put global hidden_api_policy 0
settings put global NON_DISPATCHABLE_HANDLE 25
setprop debug.showfps 0
setprop debug.showupdates 0
setprop debug.hwc.force_gpu_reset_on_hotplug true
setprop debug.sf.hwc.min.duration 0
setprop debug.windowsmgr.max_events_per_sec 240
setprop debug.egl.force_msaa false
setprop debug.egl.force_fxaa false
setprop debug.sf.hw 1
setprop debug.egl.force_taa false
setprop debug.egl.force_smaa false
setprop debug.egl.force_txaa false
setprop debug.cpurend.vsync false
setprop debug.kill_allocating_task 0
setprop debug.overlayui.enable 1
setprop debug.hwui.texture_cache_size 0
setprop debug.force_rtl false
setprop debug.hw2d.force true
setprop debug.hw3d.force true
setprop debug.hwui.render_quality low
setprop debug.egl.profiler 0
setprop debug.egl.log_config 0
setprop debug.surface_flinger.vsync_sf_event_phase_offset_ns 0
setprop debug.systemuicompilerfilter speed
setprop debug.performance.tuning 1
setprop debug.performance.profile 1
setprop debug.qcom.hw_haplite 1
setprop debug.sf.disable_client_composition_cache 1
setprop debug.hwui.composition 0
setprop debug.hwui.fps_divisor 1
setprop debug.hwui.show_draw_order 0
setprop debug.hwui.render_dirty_regions 1
setprop debug.hwui.show_dirty_regions false
setprop debug.sf.enable_gl_backpressure 1
setprop debug.stagefright.omx_default_rank.sw-audio 1
setprop debug.sf.enable_hgl 1
setprop debug.windowsmgr.max_events_per_sec 240
setprop debug.sf.enable_hwc_vds 1
setprop debug.ums.hardware true
setprop debug.sf.enable_transaction_tracing true
setprop debug.rs.qcom.use_fast_math 1
setprop debug.sf.frame_rate_multiple_threshold 3
setprop debug.sf.gpu_comp_tiling 1
setprop debug.sf.gpu_freq_index 7
setprop debug.sf.hw 0
setprop debug.sf.late.app.duration 20500000
setprop debug.sf.late.sf.duration 10500000
setprop debug.sf.max_igbp_list_size 0
setprop debug.sf.perf_fps_early_gl_phase_offset_ns 10000000
setprop debug.sf.phase_offset_threshold_for_next_vsync_ns 6100000
setprop debug.tracing.screen_state 0
setprop debug.qctwa.statusbar 1
setprop debug.gr.swapinterval 0
setprop debug.qctwa.preservebuf 1
setprop debug.qc.hardware true
setprop debug.cpu_core_ctl_active 1
setprop debug.hwui.disable_scissor_opt false
setprop debug.hwui.texture_cache_size 24
setprop debug.hwui.layer_cache_size 16
setprop debug.hwui.drop_shadow_cache_size 2
setprop debug.sf.enable_advanced_sf_phase_offset 1
setprop debug.sf.disable_backpressure 1
setprop debug.sf.latch_unsignaled 1
setprop debug.sf.high_speed_scroll_factor 10
settings put global power_check_max_cpu_1 90
settings put global power_check_max_cpu_2 90
settings put global power_check_max_cpu_3 90
settings put global power_check_max_cpu_4 90
setprop debug.gpu.scheduler_pre.emption 1
setprop debug.mdpcomp.mixedmode.disable false
setprop debug.hwc.fbsize XRESxYRES
setprop debug.sdm.support_writeback 1
setprop debug.sdm.disable_skip_validate 1
setprop debug.sf_frame_rate_multiple_fences 999
setprop debug.sf.early.app.duration 16600000
setprop debug.sf.early.sf.duration 16600000
setprop debug.sf.earlyGl.app.duration 16600000
setprop debug.sf.earlyGl.sf.duration 16600000
setprop debug.log.slow_query_threshold 150
setprop debug.sf.high_fps_early_gl_phase_offset_ns 9000000
setprop debug.sf.high_fps_early_phase_offset_ns 6100000
setprop debug.sf.hw 1
setprop debug.sf.perf_fps_early_gl_phase_offset_ns 12000000
setprop debug.composition.type mdp
"thermal-engine-8996.conf"
"thermal-engine-8996-a1.conf"
algo_type ss
sampling 250
sensor xo_therm_buff
device cluster
set_point 43000
set_point_clr 41000
time_constant 0
device_per_floor 1478400
algo_type ss
sampling 250
sensor xo_therm_buff
device cluster
set_point 45000
set_point_clr 43000
time_constant 0
device_per_floor 1113600
algo_type ss
sampling 250
sensor xo_therm_buff
device cluster
set_point 48000
set_point_clr 45000
time_constant 0
device_per_floor 940800
}
Apply_Setprop > /dev/null 2>&1
echo
echo -e "\e[94m""➤ Please Wait Applying Game Booster......"
echo " "
sleep 5s
echo
echo -e "\e[92m""➤ Please Wait......"
sleep 2
echo
sleep 0.10
echo -ne '\033[1;34m□□□□□□□□□□0% \r'
sleep 0.10
echo -ne '\033[1;34m■□□□□□□□□□10% \r'
sleep 0.10
echo -ne '\033[1;34m■■□□□□□□□□20% \r'
sleep 0.5
echo -ne '\033[1;34m■■■□□□□□□□30% \r'
sleep 0.6
echo -ne '\033[1;34m■■■■□□□□□□40% \r'
sleep 0.6
echo -ne '\033[1;34m■■■■■□□□□□50% \r'
sleep 0.10
echo -ne '\033[1;34m■■■■■■□□□□60% \r'
sleep 0.5
echo -ne '\033[1;34m■■■■■■■□□□70% \r'
sleep 0.5
echo -ne '\033[1;34m■■■■■■■■□□80% \r'
sleep 0.5
echo -ne '\033[1;34m■■■■■■■■■□90% \r'
sleep 0.5
echo -ne '\033[1;34m■■■■■■■■■■100% \r'
sleep 0.5
sleep 0.1
echo
echo
echo -e "\e[00m""➤ All Script Applied Succesfully."
echo " "
sleep 2
echo -e "\e[00m""➤ Restart Device For Better Result (Recomended)"
echo " "
echo
echo " "
sleep 0.4
echo "
╭━━━┳╮╱╭┳━━╮╭━━━┳━━━┳━━━┳━━┳━━╮╭━━━╮
┃╭━╮┃┃╱┃┃╭╮┃┃╭━╮┃╭━╮┃╭━╮┣┫┣┫╭╮┃┃╭━━╯
┃╰━━┫┃╱┃┃╰╯╰┫╰━━┫┃╱╰┫╰━╯┃┃┃┃╰╯╰┫╰━━╮
╰━━╮┃┃╱┃┃╭━╮┣━━╮┃┃╱╭┫╭╮╭╯┃┃┃╭━╮┃╭━━╯
┃╰━╯┃╰━╯┃╰━╯┃╰━╯┃╰━╯┃┃┃╰┳┫┣┫╰━╯┃╰━━╮
╰━━━┻━━━┻━━━┻━━━┻━━━┻╯╰━┻━━┻━━━┻━━━╯ Chanel Telegram @MAYKI_1_SHOP_PUBG   "
echo " "
sleep 1
echo

clear
echo -e "\e[92m"
echo "--------------------------------------"
echo "     SELECT GAME TO LAUNCH"
echo "--------------------------------------"
echo -e "\e[94m"
echo "[1] PUBG Mobile"
echo "[2] Call of Duty Mobile"
echo
# گرادیان سبز → لیمویی برای هدر ONLINE
green1='\e[38;5;40m'
green2='\e[38;5;82m'
green3='\e[38;5;118m'
reset='\e[0m'

# گرادیان صورتی → بنفش → آبی برای متن اصلی
pink='\e[38;5;198m'
purple='\e[38;5;129m'
blue='\e[38;5;63m'

# گرادیان آبی → سبز برای TERMUX
blue2='\e[38;5;39m'
green4='\e[38;5;48m'


# ─────────────────────────── هدر ONLINE ───────────────────────────
echo -e "${green1}<${green2}──────────────────────────────────────────────────${green3}>${reset}"
echo -e "                  ${green2}[★] O N L I N E [★]${reset}"
echo -e "${green1}<${green2}──────────────────────────────────────────────────${green3}>${reset}"
echo


# ─────────────────────────── متن وسط (گرادیان واقعی) ───────────────────────────
echo -e "              ${pink}__  ___                           _${reset}"
echo -e "             ${pink}/  |/  /____      ____ _____ ___  ${purple}(_)___${reset}"
echo -e "            ${pink}/ /|_/ / ___/_____/ __ \`/ __ \`__ \\/${purple} / __ \\${reset}"
echo -e "           ${purple}/ /  / / /  /_____/ /_/ / / / / / /${blue} / / / /${reset}"
echo -e "          ${blue}/_/  /_/_/         \\__,_/_/ /_/ /_/_/${blue}_/_/ /_/${reset}"
echo


# ─────────────────────────── فوتر TERMUX ───────────────────────────
echo -e "        ${blue2}<${green4}──────────────────────────────────────────────────${blue2}>${reset}"
echo -e "                  ${blue2}[★] T E R M U X [★]${reset}"
echo -e "        ${blue2}<${green4}──────────────────────────────────────────────────${blue2}>${reset}"

echo -ne "\e[92mENTER NUMBER: \e[0m"
read game

case $game in
    1)
        echo -e "\e[92mOpening PUBG Mobile...\e[0m"
        am start -n com.tencent.ig/com.epicgames.ue4.SplashActivity
        ;;
    2)
        echo -e "\e[92mOpening Call of Duty Mobile...\e[0m"
        am start -n com.activision.callofduty.shooter/com.unity3d.player.UnityPlayerActivity
        ;;
    *)
        echo -e "\e[91mInvalid option!\e[0m"
        ;;
esac

exit
