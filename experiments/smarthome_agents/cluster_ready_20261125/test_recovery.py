#!/usr/bin/env python3
"""Controlled recovery/selection checks on only the new isolated services."""
import json,time
from pathlib import Path
import provision,select_host,validate_profiles
HERE=Path(__file__).resolve().parent
pool=json.loads((HERE/'pool.json').read_text())
out={}
# The previous validation must have completed before intentional disruptions.
assert all(r['ready'] and r['restored_05'] for r in json.loads((HERE/'validation.json').read_text()))
reserve='192.168.50.85'
unit='smarthome-benchmark-05.service'
before=provision.ssh(reserve,'systemctl show '+unit+' -p MainPID --value').strip()
provision.ssh(reserve,'sudo -n systemctl kill --kill-whom=main --signal=SIGTERM '+unit)
start=time.monotonic()
for _ in range(180):
 after=provision.ssh(reserve,'systemctl show '+unit+' -p MainPID --value').strip()
 if after not in ['0',before]:
  try:
   props=validate_profiles.wait(reserve,'05');break
  except Exception:pass
 time.sleep(1)
else:raise RuntimeError('Service did not recover')
out['automatic_service_restart']={'ip':reserve,'old_pid':before,'new_pid':after,'health_recovered':True,'elapsed_s':time.monotonic()-start}
primary=pool['boards'][0]
try:
 provision.ssh(primary['ip'],'sudo -n systemctl stop '+unit)
 regular=select_host.select(pool)
 assert regular['selected'] and regular['selected']['ip']!=primary['ip']
 out['primary_unavailable_selects_next_primary']=regular
 limited=dict(pool);limited['boards']=[primary]+[b for b in pool['boards'] if b['role']=='reserve']
 fallback=select_host.select(limited)
 assert fallback['selected'] and fallback['selected']['role']=='reserve'
 out['no_available_primary_selects_reserve']=fallback
finally:
 provision.ssh(primary['ip'],'sudo -n systemctl start '+unit)
 validate_profiles.wait(primary['ip'],'05')
 out['primary_restored']=True
out['final_full_pool']=select_host.select(pool)
assert all(r['ready'] for r in out['final_full_pool']['checks'])
(HERE/'recovery_test.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'automatic_restart':True,'alternate_primary':regular['selected']['ip'],'reserve_fallback':fallback['selected']['ip'],'all_seven_restored':True}))
