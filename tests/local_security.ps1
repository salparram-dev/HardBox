# Comprueba que se cumple:
# "MinimumPasswordLength = 10",
# "PasswordComplexity = 1",
# "MaximumPasswordAge = 60",
# "MinimumPasswordAge = 1",
# "PasswordHistorySize = 10",
# "LockoutBadCount = 5",
# "ResetLockoutCount = 15",
# "LockoutDuration = 15",
secedit /export /cfg C:\temp\resultado_seg_local.inf /areas SECURITYPOLICY
notepad C:\temp\resultado_seg_local.inf
