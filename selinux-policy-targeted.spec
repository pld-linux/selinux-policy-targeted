%define	type	targeted
Summary:	SELinux %{type} policy configuration
Summary(pl):	Konfiguracja polityki %{type} SELinuksa
Name:		selinux-policy-%{type}
Version:	1.16
Release:	1
License:	GPL
Group:		Base
Source0:	http://www.nsa.gov/selinux/archives/policy-%{version}.tgz
# Source0-md5:	bd781c50d259f8c7610cbcebaaff884d
#Source1:	%{name}-booleans
#Patch0:		policy-%{type}.patch
#Patch1:		policy-20040915.patch
BuildRequires:	checkpolicy >= 1.16.3
BuildRequires:	m4
BuildRequires:	policycoreutils >= 1.17.2-1
BuildRequires:	python
Obsoletes:	policy
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Security-enhanced Linux is a patch of the Linux kernel and a number
of utilities with enhanced security functionality designed to add
mandatory access controls to Linux. The Security-enhanced Linux kernel
contains new architectural components originally developed to improve
the security of the Flask operating system. These architectural
components provide general support for the enforcement of many kinds
of mandatory access control policies, including those based on the
concepts of Type Enforcement, Role-based Access Control, and
Multi-level Security.

This package contains the SELinux example policy configuration along
with the Flask configuration information and the application
configuration files.

%description -l pl
Security-enhanced Linux jest poprawk� j�dra Linuksa i wielu
aplikacji u�ytkowych o funkcjach podwy�szonego bezpiecze�stwa.
Zaprojektowany jest tak, aby w prosty spos�b ukaza� znaczenie
mandatowej kontroli dost�pu dla spo�eczno�ci Linuksowej. Ukazuje
r�wnie� jak tak� kontrol� mo�na doda� do istniej�cego systemu typu
Linux. J�dro SELinux zawiera nowe sk�adniki architektury pierwotnie
opracowane w celu ulepszenia bezpiecze�stwa systemu operacyjnego
Flask. Te elementy zapewniaj� og�lne wsparcie we wdra�aniu wielu typ�w
polityk mandatowej kontroli dost�pu, w��czaj�c te wzorowane na: Type
Enforcement, kontroli dost�pu opartej na rolach i zabezpieczeniach
wielopoziomowych.

Ten pakiet zawiera przyk�adow� konfiguracj� polityki dla SELinuksa
wraz z informacjami o konfiguracji Flask oraz plikami konfiguracyjnymi
aplikacji.

%package sources
Summary:	SELinux example policy configuration source files
Summary(pl):	Pliki �r�d�owe przyk�adowej konfiguracji polityki SELinuksa
Group:		Base
Requires:	%{name} = %{version}-%{release}
Requires:	m4
Requires:	make
Requires:	checkpolicy >= 1.16
Requires:	policycoreutils >= 1.16
Requires:	python
Obsoletes:	policy-sources

%description sources
This subpackage includes the source files used to build the policy
configuration. Includes policy.conf and the Makefiles, macros and
source files for it.

%description sources -l pl
Ten podpakiet zawiera pliki �r�d�owe u�yte do zbudowania konfiguracji
polityki. Zawiera policy.conf oraz wszystkie Makefile, makra i pliki
�r�d�owe.

%prep
%setup -q -n policy-%{version}
# Change strict to targeted
#%%patch -p1
#%%patch1 -p1

%build
mv domains/misc/*.te domains/misc/unused
mv domains/program/*.te domains/program/unused/
rm domains/*.te
for i in nscd.te apache.te dhcpd.te named.te ntpd.te portmap.te snmpd.te squid.te syslogd.te; do
mv domains/program/unused/$i domains/program/
done
rm -rf domains/program/unused
rm -rf domains/misc/used
cp -R %{type}/* .
echo "define(\`targeted_policy')" > tunables/tunable.tun
echo "define(\`allow_ypbind')" >> tunables/tunable.tun
echo "define(\`nscd_all_connect')" >> tunables/tunable.tun
%{__make} policy

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/root
install -d $RPM_BUILD_ROOT%{_sysconfdir}/selinux/%{type}/contexts/users
install -d $RPM_BUILD_ROOT%{_sysconfdir}/selinux/%{type}/contexts/files
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
%{__make} clean
%{__make} install-src \
	DESTDIR=$RPM_BUILD_ROOT
rm -rf "$RPM_BUILD_ROOT%{_sysconfdir}/selinux/%{type}/src/policy/targeted"
rm -rf "$RPM_BUILD_ROOT%{_sysconfdir}/selinux/%{type}/src/policy"/*.spec
install -m0700 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/selinux/%{type}/
touch $RPM_BUILD_ROOT%{_sysconfdir}/selinux/%{type}/src/policy/policy.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/selinux/config

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f /etc/selinux/config ]; then
		#
		#	New install so we will default to targeted policy
		#
		echo "
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#	enforcing - SELinux security policy is enforced.
#	permissive - SELinux prints warnings instead of enforcing.
#	disabled - No SELinux policy is loaded.
SELINUX=enforcing
# SELINUXTYPE= can take one of these two values:
#	targeted - Only targeted network daemons are protected.
#	strict - Full SELinux protection.
SELINUXTYPE=targeted " > /etc/selinux/config

	fi
fi
ln -sf /etc/selinux/config /etc/sysconfig/selinux
restorecon /etc/selinux/config

if [ -x /usr/bin/selinuxenabled ] && /usr/bin/selinuxenabled && [ -e /selinux/policyvers ]; then
	. /etc/selinux/config
	if [ "${SELINUXTYPE}" = "%{type}" ]; then
		/usr/sbin/load_policy /etc/selinux/%{type}/policy/policy.`cat /selinux/policyvers`
	fi
fi
exit 0

%post sources
if [ -x /usr/bin/selinuxenabled ]; then
	make -W /etc/selinux/%{type}/src/policy/users \
		-C /etc/selinux/%{type}/src/policy > /dev/null 2>&1
	if [ -f /etc/selinux/config ]; then
		. /etc/selinux/config
		if [ "${SELINUXTYPE}" = "%{type}" ]; then
			/usr/bin/selinuxenabled && [ -e /selinux/policyvers ] \
				&& make -C /etc/selinux/%{type}/src/policy load
		fi
	fi
fi
exit 0

%files
%defattr(644,root,root,755)
%dir %{_sysconfdir}/selinux
%ghost %config(noreplace) %{_sysconfdir}/selinux/config
%dir %{_sysconfdir}/selinux/%{type}
%dir %{_sysconfdir}/selinux/%{type}/policy
%dir %{_sysconfdir}/selinux/%{type}/contexts
%dir %{_sysconfdir}/selinux/%{type}/contexts/files
%dir %{_sysconfdir}/selinux/%{type}/contexts/users
%config %{_sysconfdir}/selinux/%{type}/booleans
%config(noreplace) %{_sysconfdir}/selinux/%{type}/policy/policy\.*
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/files/file_contexts
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/files/media
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/default_contexts
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/default_type
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/initrc_context
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/failsafe_context
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/userhelper_context
%config(noreplace) %{_sysconfdir}/selinux/%{type}/contexts/users/root

%files sources
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/selinux/%{type}/src/policy/users
%dir %{_sysconfdir}/selinux/%{type}/src/policy/tunables
%config %{_sysconfdir}/selinux/%{type}/src/policy/tunables/*.tun
%dir %{_sysconfdir}/selinux/%{type}/src
%dir %{_sysconfdir}/selinux/%{type}/src/policy
%{_sysconfdir}/selinux/%{type}/src/policy/ChangeLog
%{_sysconfdir}/selinux/%{type}/src/policy/COPYING
%{_sysconfdir}/selinux/%{type}/src/policy/Makefile
%{_sysconfdir}/selinux/%{type}/src/policy/README
%{_sysconfdir}/selinux/%{type}/src/policy/VERSION
%dir %{_sysconfdir}/selinux/%{type}/src/policy/appconfig
%config %{_sysconfdir}/selinux/%{type}/src/policy/appconfig/*
%config %{_sysconfdir}/selinux/%{type}/src/policy/assert.te
%config %{_sysconfdir}/selinux/%{type}/src/policy/attrib.te
%config %{_sysconfdir}/selinux/%{type}/src/policy/constraints
%dir %{_sysconfdir}/selinux/%{type}/src/policy/domains
%config %{_sysconfdir}/selinux/%{type}/src/policy/domains/*
%dir %{_sysconfdir}/selinux/%{type}/src/policy/file_contexts
%config %{_sysconfdir}/selinux/%{type}/src/policy/file_contexts/*
%dir %{_sysconfdir}/selinux/%{type}/src/policy/flask
%config %{_sysconfdir}/selinux/%{type}/src/policy/flask/*
%config %{_sysconfdir}/selinux/%{type}/src/policy/fs_use
%config %{_sysconfdir}/selinux/%{type}/src/policy/genfs_contexts
%config %{_sysconfdir}/selinux/%{type}/src/policy/initial_sid_contexts
%dir %{_sysconfdir}/selinux/%{type}/src/policy/macros
%config %{_sysconfdir}/selinux/%{type}/src/policy/macros/*
%config %{_sysconfdir}/selinux/%{type}/src/policy/mls
%config %{_sysconfdir}/selinux/%{type}/src/policy/net_contexts
%config %{_sysconfdir}/selinux/%{type}/src/policy/rbac
%config %{_sysconfdir}/selinux/%{type}/src/policy/serviceusers
%dir %{_sysconfdir}/selinux/%{type}/src/policy/types
%config %{_sysconfdir}/selinux/%{type}/src/policy/types/*
%ghost %{_sysconfdir}/selinux/%{type}/src/policy/policy.conf
%ghost %{_sysconfdir}/selinux/%{type}/src/policy/tmp
