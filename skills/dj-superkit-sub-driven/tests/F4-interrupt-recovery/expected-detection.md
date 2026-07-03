# F4-interrupt-recovery
세션 시작 시 `detect_stale_buffer(root, "F4")` 호출 결과:
- root/F4 디렉토리 존재 + task-01.md task-02.md 잔존
- 반환: `<root>/F4` (Path)
- 사용자에게 복구 prompt 노출되어야 함
