%define USE_FIPSCHECK 1
%define USE_LIBCAP_NG 1
%define USE_LABELED_IPSEC 1
%define USE_CRL_FETCHING 1
%define USE_DNSSEC 1
%define USE_NM 1

%define fipscheck_version 1.2.0-1
%define buildklips 0
%define buildefence 0
%define development 0

Name: libreswan
Summary: IPsec implementation with IKEv1 and IKEv2 keying protocols
# version is generated in the release script
Version: IPSECBASEVERSION

# The default kernel version to build for is the latest of
# the installed binary kernel
# This can be overridden by "--define 'kversion x.x.x-y.y.y'"
%define defkv %(rpm -q kernel kernel-debug| grep -v "not installed" | sed -e "s/kernel-debug-//" -e  "s/kernel-//" -e "s/\.[^.]*$//"  | sort | tail -1 )
%{!?kversion: %{expand: %%define kversion %defkv}}
%define krelver %(echo %{kversion} | tr -s '-' '_')
# Libreswan -pre/-rc nomenclature has to co-exist with hyphen paranoia
%define srcpkgver %(echo %{version} | tr -s '_' '-')

Release: 1%{?dist}
License: GPLv2
Url: http://www.libreswan.org/
Source: %{name}-%{srcpkgver}.tar.gz
Group: System Environment/Daemons
BuildRequires: gmp-devel bison flex redhat-rpm-config pkgconfig
Requires(post): coreutils bash
Requires(preun): initscripts chkconfig
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

BuildRequires: pkgconfig net-tools
BuildRequires: nss-devel >= 3.12.6-2, nspr-devel
BuildRequires: pam-devel
%if %{USE_DNSSEC}
BuildRequires: unbound-devel
%endif
%if %{USE_FIPSCHECK}
BuildRequires: fipscheck-devel >= %{fipscheck_version}
# we need fipshmac
Requires: fipscheck%{_isa} >= %{fipscheck_version}
%endif
%if %{USE_LIBCAP_NG}
BuildRequires: libcap-ng-devel
%endif
%if %{USE_CRL_FETCHING}
BuildRequires: openldap-devel curl-devel
%endif
%if %{buildefence}
BuildRequires: ElectricFence
%endif
# Only needed if xml man pages are modified and need regeneration
# BuildRequires: xmlto

Requires: nss-tools, nss-softokn
Requires: iproute >= 2.6.8

%description
Libreswan is a free implementation of IPsec & IKE for Linux.  IPsec is 
the Internet Protocol Security and uses strong cryptography to provide
both authentication and encryption services.  These services allow you
to build secure tunnels through untrusted networks.  Everything passing
through the untrusted net is encrypted by the ipsec gateway machine and 
decrypted by the gateway at the other end of the tunnel.  The resulting
tunnel is a virtual private network or VPN.

This package contains the daemons and userland tools for setting up
Libreswan. It optionally also builds the Libreswan KLIPS IPsec stack that
is an alternative for the NETKEY/XFRM IPsec stack that exists in the
default Linux kernel.

Libreswan also supports IKEv2 (RFC4309) and Secure Labeling

Libreswan is based on Openswan-2.6.38 which in turn is based on FreeS/WAN-2.04

%if %{buildklips}
%package klips
Summary: Libreswan kernel module
Group:  System Environment/Kernel
Release: %{krelver}_%{release}
Requires: kernel = %{kversion}, %{name}-%{version}

%description klips
This package contains only the ipsec module for the RedHat/Fedora series of
kernels.
%endif

%prep
%setup -q -n libreswan-%{srcpkgver}

%build
%if %{buildefence}
 %define efence "-lefence"
%endif

#796683: -fno-strict-aliasing
%{__make} \
%if %{development}
   USERCOMPILE="-g -DGCC_LINT %(echo %{optflags} | sed -e s/-O[0-9]*/ /) %{?efence} -fPIE -pie -fno-strict-aliasing" \
%else
  USERCOMPILE="-g -DGCC_LINT %{optflags} %{?efence} -fPIE -pie -fno-strict-aliasing" \
%endif
  INITSYSTEM=sysvinit \
  USERLINK="-g -pie %{?efence}" \
  USE_DYNAMICDNS="true" \
  USE_NM=%{USE_NM} \
  USE_XAUTHPAM=true \
  USE_FIPSCHECK="%{USE_FIPSCHECK}" \
  USE_LIBCAP_NG="%{USE_LIBCAP_NG}" \
  USE_LABELED_IPSEC="%{USE_LABELED_IPSEC}" \
%if %{USE_CRL_FETCHING}
  USE_LDAP=true \
  USE_LIBCURL=true \
%endif
  USE_DNSSEC="%{USE_DNSSEC}" \
  INC_USRLOCAL=%{_prefix} \
  FINALLIBDIR=%{_libexecdir}/ipsec \
  FINALLIBEXECDIR=%{_libexecdir}/ipsec \
  MANTREE=%{_mandir} \
  INC_RCDEFAULT=%{_initrddir} \
  programs
FS=$(pwd)

%if %{USE_FIPSCHECK}
# Add generation of HMAC checksums of the final stripped binaries
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
  fipshmac $RPM_BUILD_ROOT%{_sbindir}/ipsec \
  fipshmac $RPM_BUILD_ROOT%{_libexecdir}/ipsec/* \
%{nil}
%endif

%if %{buildklips}
mkdir -p BUILD.%{_target_cpu}

cd packaging/fedora
# rpm doesn't know we're compiling kernel code. optflags will give us -m64
%{__make} -C $FS MODBUILDDIR=$FS/BUILD.%{_target_cpu} \
    LIBRESWANSRCDIR=$FS \
    INITSYSTEM=sysvinit \
    KLIPSCOMPILE="%{optflags}" \
    KERNELSRC=/lib/modules/%{kversion}/build \
    ARCH=%{_arch} \
    MODULE_DEF_INCLUDE=$FS/packaging/fedora/config-%{_target_cpu}.h \
    MODULE_EXTRA_INCLUDE=$FS/packaging/fedora/extra_%{krelver}.h \
    include module
%endif

%install
rm -rf ${RPM_BUILD_ROOT}
%{__make} \
  DESTDIR=$RPM_BUILD_ROOT \
  INITSYSTEM=sysvinit \
  INC_USRLOCAL=%{_prefix} \
  FINALLIBDIR=%{_libexecdir}/ipsec \
  FINALLIBEXECDIR=%{_libexecdir}/ipsec \
  MANTREE=$RPM_BUILD_ROOT%{_mandir} \
  INC_RCDEFAULT=%{_initrddir} \
  INSTMANFLAGS="-m 644" \
  install
FS=$(pwd)
rm -rf $RPM_BUILD_ROOT/usr/share/doc/libreswan

install -d -m 0700 $RPM_BUILD_ROOT%{_localstatedir}/run/pluto
# used when setting --perpeerlog without --perpeerlogbase 
install -d -m 0700 $RPM_BUILD_ROOT%{_localstatedir}/log/pluto/peer
install -d $RPM_BUILD_ROOT%{_sbindir}

%if %{buildklips}
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{kversion}/kernel/net/ipsec
for i in $FS/BUILD.%{_target_cpu}/ipsec.ko  $FS/modobj/ipsec.o
do
  if [ -f $i ]
  then
    cp $i $RPM_BUILD_ROOT/lib/modules/%{kversion}/kernel/net/ipsec 
  fi
done
%endif

echo "include /etc/ipsec.d/*.secrets" > $RPM_BUILD_ROOT/%{_sysconfdir}/ipsec.secrets
rm -fr $RPM_BUILD_ROOT/etc/rc.d/rc*

%files 
%doc BUGS CHANGES COPYING CREDITS README LICENSE
%doc docs/*.*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ipsec.conf
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ipsec.secrets
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/pluto
%attr(0700,root,root) %dir %{_sysconfdir}/ipsec.d
%attr(0700,root,root) %dir %{_localstatedir}/log/pluto/peer
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/ipsec.d/policies/*
%attr(0700,root,root) %dir %{_localstatedir}/run/pluto
%{_sysconfdir}/pam.d/pluto
%{_initrddir}/ipsec
%{_libexecdir}/ipsec
%{_sbindir}/ipsec
%{_mandir}/*/*.gz

%if %{USE_FIPSCHECK}
%{_sbindir}/.ipsec.hmac
%endif

%if %{buildklips}
%files klips
/lib/modules/%{kversion}/kernel/net/ipsec
%endif

%preun
if [ $1 -eq 0 ]; then
        /sbin/service ipsec stop > /dev/null 2>&1 || :
        /sbin/chkconfig --del ipsec
fi

%postun
if [ $1 -ge 1 ] ; then
 /sbin/service ipsec condrestart 2>&1 >/dev/null || :
fi

%if %{buildklips}
%postun klips
/sbin/depmod -ae %{kversion}
%post klips
/sbin/depmod -ae %{kversion}
%endif

%post 
/sbin/chkconfig --add ipsec || :

%changelog
* Tue Jan 01 2013 Libreswan Team <team@libreswan.org> - IPSECBASEVERSION-1
- Automated build from release tar ball

