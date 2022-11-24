Name:                gearmand
Version:             1.1.19.1
Release:             2
Summary:             A distributed job system
License:             BSD
URL:                 http://www.gearman.org
Source0:             https://github.com/gearman/%{name}/releases/download/%{version}/gearmand-%{version}.tar.gz
Source1:             gearmand.init
Source2:             gearmand.sysconfig
Source3:             gearmand.service
Patch0:              gearmand-1.1.12-ppc64le.patch
Patch1:              https://github.com/gearman/gearmand/pull/273.patch
Patch1000:           add-riscv64-support.patch
ExcludeArch:         ppc
BuildRequires:       gcc-c++ chrpath libuuid-devel boost-devel >= 1.37.0, boost-thread sqlite-devel
BuildRequires:       tokyocabinet-devel libevent-devel libmemcached-devel, memcached hiredis-devel
BuildRequires:       gperf mariadb-connector-c-devel openssl-devel libpq-devel zlib-devel systemd
%ifarch %{ix86} x86_64 ppc64 ppc64le aarch64 %{arm}
BuildRequires:       gperftools-devel
%endif
Requires(pre):  shadow-utils
Requires:            procps
%{?systemd_requires}
%description
Gearman provides a generic framework to farm out work to other machines
or dispatch function calls to machines that are better suited to do the work.
It allows you to do work in parallel, to load balance processing, and to
call functions between languages. It can be used in a variety of applications,
from high-availability web sites to the transport for database replication.
In other words, it is the nervous system for how distributed processing
communicates.

%package -n libgearman
Summary:             Development libraries for gearman
Provides:            libgearman-1.0 = %{version}-%{release}
Obsoletes:           libgearman-1.0 < %{version}-%{release}
%description -n libgearman
Development libraries for %{name}.

%package -n libgearman-devel
Summary:             Development headers for libgearman
Requires:            pkgconfig, libgearman = %{version}-%{release} libevent-devel
Provides:            libgearman-1.0-devel = %{version}-%{release}
Obsoletes:           libgearman-1.0-devel < %{version}-%{release}
%description -n libgearman-devel
Development headers for %{name}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%ifarch riscv64
%patch1000 -p1
%endif

%build
%configure --disable-static --disable-silent-rules --enable-ssl
make %{_smp_mflags}

%install
make install DESTDIR=%{buildroot}
rm -v %{buildroot}%{_libdir}/libgearman*.la
chrpath --delete %{buildroot}%{_bindir}/gearman
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/gearmand
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

%check

%pre
getent group gearmand >/dev/null || groupadd -r gearmand
getent passwd gearmand >/dev/null || \
        useradd -r -g gearmand -d / -s /sbin/nologin \
        -c "Gearmand job server" gearmand
exit 0

%post
%systemd_post gearmand.service

%preun
%systemd_preun gearmand.service

%postun
%systemd_postun_with_restart gearmand.service
%ldconfig_scriptlets -n libgearman

%files
%license COPYING
%doc AUTHORS ChangeLog HACKING THANKS
%config(noreplace) %{_sysconfdir}/sysconfig/gearmand
%{_sbindir}/gearmand
%{_bindir}/gearman
%{_bindir}/gearadmin
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_unitdir}/%{name}.service

%files -n libgearman
%license COPYING
%{_libdir}/libgearman.so.8
%{_libdir}/libgearman.so.8.0.0

%files -n libgearman-devel
%license COPYING
%doc AUTHORS ChangeLog HACKING THANKS
%dir %{_includedir}/libgearman
%{_includedir}/libgearman/
%{_libdir}/pkgconfig/gearmand.pc
%{_libdir}/libgearman.so
%{_includedir}/libgearman-1.0/
%{_mandir}/man3/*

%changelog
* Thu Nov 24 2022 misaka00251 <liuxin@iscas.ac.cn> - 1.1.19.1-2
- Fix build on riscv64

* Tue Sep 7 2021 zhengyaohui <zhengyaohui1@huawei.com> - 1.1.19.1-1
- package init
