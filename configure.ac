#                                               -*- Autoconf -*-
# This template is inspired from autowritten example by autoscan
# Please using `autoscan' you could be more satisfied
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.64])
AC_INIT([DjangoContribAderit], [1.4.6], [tecnici@aderit.it])
AC_COPYRIGHT([Copyright (C) 2012 Aderit srl])
AC_CONFIG_SRCDIR([django/contrib/aderit/__init__.py])

# Checks for programs.
AC_PROG_GREP

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

################
AC_SUBST(PACKAGE_DESCRIPTION, ["Collection of Aderit tools for Django"])
AC_SUBST(AUTHOR, ["Matteo Atti"])
AC_SUBST(AUTHOR_EMAIL, [matteo.atti@aderit.it])


if ! grep native debian/source/format ; then
   AC_CONFIG_COMMANDS([source], [debian/rules get-orig-source])
else
   echo Debian native package, no get-orig-source
fi

dnl AC_CONFIG_COMMANDS_POST([rm configure])
# debian/changelog.in stuff
dnl AC_ARG_ENABLE([release],[dnl
dnl AS_HELP_STRING([--enable-release],
dnl        [do debian release (default is no)])],
dnl [do_release=yes], [do_release=no])
AC_ARG_WITH([release],[dnl
AS_HELP_STRING([--with-release],
               [do debian release (default is UNRELEASED)])],
	[do_release=yes release=$withval], [do_release=no release=UNRELEASED])

AC_ARG_WITH([urgency],[dnl
AS_HELP_STRING([--with-urgency],
               [do debian urgency (default is low)])],
	[urgency=$withval], [urgency=low])

m4_define([MAKE_DEBIAN_CHANGELOG_IN],[dnl
if test -r debian/changelog.git ; then
   cp debian/changelog.git debian/changelog.in.in
else
   dch --create -c debian/changelog.git
fi
AS_ECHO_N("@DEBIAN_PACKAGE@") >debian/changelog.in
AS_ECHO_N(" (@PACKAGE_VERSION@@VERSION_SUFFIX@) ") >>debian/changelog.in
AS_ECHO("@UNRELEASED@; urgency=@URGENCY@") >>debian/changelog.in
AS_ECHO >>debian/changelog.in
AS_ECHO("  * @DEB_MSG@") >>debian/changelog.in
AS_ECHO >>debian/changelog.in
AS_ECHO(" -- @AUTHOR@ <@AUTHOR_EMAIL@>  @DATE_TIME@") >>debian/changelog.in
AS_ECHO >>debian/changelog.in
test -r debian/changelog.in.in && cat debian/changelog.in.in >>debian/changelog.in
])

MAKE_DEBIAN_CHANGELOG_IN

AC_SUBST(UNRELEASED, [$release])
AC_SUBST(URGENCY, [$urgency])

AC_SUBST(DEB_MSG, [`git rev-list -n1 --oneline HEAD`])
AC_SUBST(DEBIAN_PACKAGE, [django-contrib-aderit])

if test x"$do_release" != x"yes" ; then
  deb_version_suffix="+`git rev-list -n1 --oneline HEAD | cut -d' ' -f1`"
else
  deb_version_suffix=
fi
AC_SUBST(VERSION_SUFFIX, [$deb_version_suffix])
AC_SUBST(DATE_TIME, [`date --rfc-2822`])

AC_OUTPUT([
	setup.py
	debian/changelog
])
