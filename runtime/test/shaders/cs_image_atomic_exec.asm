; 8 lanes address distinct texels. The even lanes add 7 with glc to row zero and 11 without glc to row one.
; After restoring EXEC, copy both data registers to the signed image. Row zero gets the old texel in active
; lanes and the original 7 in inactive lanes. Row one keeps 11 in all lanes because glc was clear.
; The uint image starts at 100+i and the sint image at -2i. Neither image changes beyond those two rows.
; group: 8,1,1
; mattr: +wavefrontsize32,-wavefrontsize64
; Run: vk_store_test cs_image_atomic_exec.spv words
s_mov_b32 s8, 0x2000
s_mov_b32 s9, 0x1400000
s_mov_b32 s10, 0x22
s_mov_b32 s11, 0x22
s_mov_b32 s12, 0x22
s_mov_b32 s13, 0x22
s_mov_b32 s14, 0x22
s_mov_b32 s15, 0x22
s_mov_b32 s16, 0x3000
s_mov_b32 s17, 0x1500000
s_mov_b32 s18, 0x33
s_mov_b32 s19, 0x33
s_mov_b32 s20, 0x33
s_mov_b32 s21, 0x33
s_mov_b32 s22, 0x33
s_mov_b32 s23, 0x33

v_mov_b32_e32 v1, v0
v_mov_b32_e32 v2, 0
v_mov_b32_e32 v3, 7
v_mov_b32_e32 v4, 11
v_and_b32_e32 v5, 1, v0
v_cmpx_eq_u32_e32 0, v5
image_atomic_add v3, v[1:2], s[8:15] dmask:0x1 dim:SQ_RSRC_IMG_2D unorm glc
v_mov_b32_e32 v2, 1
image_atomic_add v4, v[1:2], s[8:15] dmask:0x1 dim:SQ_RSRC_IMG_2D unorm
s_waitcnt vmcnt(0)
s_mov_b32 exec_lo, -1

v_mov_b32_e32 v2, 0
image_store v3, v[1:2], s[16:23] dmask:0x1 dim:SQ_RSRC_IMG_2D unorm
v_mov_b32_e32 v2, 1
image_store v4, v[1:2], s[16:23] dmask:0x1 dim:SQ_RSRC_IMG_2D unorm
s_endpgm
