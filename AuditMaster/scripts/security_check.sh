#!/bin/bash

echo "=================================="
echo "       AUDITMASTER SECURITY CHECK"
echo "=================================="

echo ""
echo "1. AUDITD SERVICE STATUS"
systemctl is-active auditd

echo ""
echo "2. SAMBA SERVICE STATUS"
systemctl is-active smbd

echo ""
echo "3. DEPARTMENT FOLDER PERMISSIONS"
ls -ld /srv/auditmaster/CSE
ls -ld /srv/auditmaster/ECE
ls -ld /srv/auditmaster/IT

echo ""
echo "4. DISK QUOTA STATUS"
repquota -g /mnt/auditmaster-quota

echo ""
echo "5. AIDE VERSION"
aide --version | head -n 1

echo ""
echo "=================================="
echo "       SECURITY CHECK COMPLETED"
echo "=================================="
