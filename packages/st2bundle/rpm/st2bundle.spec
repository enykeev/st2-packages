%define package st2bundle
%define venv_name st2
%define svc_user st2
%define stanley_user stanley
%include ../rpmspec/st2pkg_toptags.spec

Summary: StackStorm all components bundle
Conflicts: st2common

%description
  Package is full standalone stackstorm installation including
  all components

# Define worker name
%define worker_name %{!?use_systemd:st2actionrunner-worker}%{?use_systemd:st2actionrunner@}


%install
  %default_install
  %pip_install_venv
  %service_install st2actionrunner %{worker_name} st2api st2auth st2exporter
  %service_install st2notifier st2resultstracker st2rulesengine st2sensorcontainer
  make post_install DESTDIR=%{?buildroot}
  # clean up absolute path in record file, so that /usr/bin/check-buildroot doesn't fail
  find /root/rpmbuild/BUILDROOT/%{package}* -name RECORD -exec sed -i '/\/root\/rpmbuild.*$/d' '{}' ';'

%prep
  rm -rf %{buildroot}
  mkdir -p %{buildroot}

%clean
  rm -rf %{buildroot}

%pre
  # handle installation (not upgrade)
  if [ $1 = 1 ]; then
    [ -f /etc/logrotate.d/st2.disabled ] && mv -f /etc/logrotate.d/st2.disabled /etc/logrotate.d/st2
  fi
  adduser --no-create-home --system %{svc_user} 2>/dev/null
  adduser --user-group %{stanley_user} 2>/dev/null
  exit 0

%post
  if [ ! -f /etc/st2/htpasswd ]; then
    touch /etc/st2/htpasswd
    chown %{svc_user}.%{svc_user} /etc/st2/htpasswd
    chmod 640 /etc/st2/htpasswd
  fi
  %service_post st2actionrunner %{worker_name} st2api st2auth st2exporter
  %service_post st2notifier st2resultstracker st2rulesengine st2sensorcontainer

%preun
  %service_preun st2actionrunner %{worker_name} st2api st2auth st2exporter
  %service_preun st2notifier st2resultstracker st2rulesengine st2sensorcontainer

%postun
  %service_postun st2actionrunner %{worker_name} st2api st2auth st2exporter
  %service_postun st2notifier st2resultstracker st2rulesengine st2sensorcontainer
  # rpm has no purge option, so we leave this file
  [ -f /etc/logrotate.d/st2 ] && mv -f /etc/logrotate.d/st2 /etc/logrotate.d/st2.disabled
  exit 0

%files
  %defattr(-,root,root,-)
  %{_bindir}/*
  %config(noreplace) %{_sysconfdir}/logrotate.d/st2
  %config(noreplace) %{_sysconfdir}/st2/*
  %{_datadir}/python/%{venv_name}
  %{_datadir}/doc/st2/examples
  %attr(755, %{svc_user}, %{svc_user}) %{_localstatedir}/log/st2
  /opt/stackstorm/packs/core
  /opt/stackstorm/packs/linux
  /opt/stackstorm/packs/packs
  %attr(755, %{svc_user}, %{svc_user}) /opt/stackstorm/exports
%if 0%{?use_systemd}
  %{_unitdir}/st2actionrunner.service
  %{_unitdir}/%{worker_name}.service
  %{_unitdir}/st2api.service
  %{_unitdir}/st2auth.service
  %{_unitdir}/st2exporter.service
  %{_unitdir}/st2notifier.service
  %{_unitdir}/st2resultstracker.service
  %{_unitdir}/st2rulesengine.service
  %{_unitdir}/st2sensorcontainer.service
%else
  %{_sysconfdir}/rc.d/init.d/st2actionrunner
  %{_sysconfdir}/rc.d/init.d/%{worker_name}
  %{_sysconfdir}/rc.d/init.d/st2api
  %{_sysconfdir}/rc.d/init.d/st2auth
  %{_sysconfdir}/rc.d/init.d/st2exporter
  %{_sysconfdir}/rc.d/init.d/st2notifier
  %{_sysconfdir}/rc.d/init.d/st2resultstracker
  %{_sysconfdir}/rc.d/init.d/st2rulesengine
  %{_sysconfdir}/rc.d/init.d/st2sensorcontainer
%endif
