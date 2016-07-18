%%%%% http://www.latex-project.org/guides/clsguide.pdf
\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{premigration}[2016/07/01 Haug's custom Class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions\relax

\typeout{-----------------------------------------------------------}

\LoadClass[12pt]{report}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{pytex}

\fancyhead{}
\fancyfoot{}

\lhead{Pre-migration Report}
%\rhead{\today}

\cfoot{\thepage}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\endinput
