%%%%% http://www.latex-project.org/guides/clsguide.pdf
\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{premigration}[2016/07/01 Haug's custom Class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}}
\ProcessOptions\relax

\typeout{-----------------------------------------------------------}

\LoadClass[12pt]{report}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{pytex}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\renewcommand{\maketitle}{%
{\fontsize{24}{30}\fontfamily{phv}\fontseries{b}%
\fontshape{sl}\selectfont\color{palette1}
\@title
}

{\fontsize{18}{20}\fontfamily{phv}\fontseries{b}%
\fontshape{sl}\selectfont\color{palette1light}
\@author
}}

%%%%%%%%%%%%

\renewcommand{\section}{%
\@startsection
{section}{1}{0pt}{-1.5ex plus -1ex minus -.2ex}%
{1ex plus .2ex}{\large\sffamily\color{palette1}}%
}

%%%%%%%%%%%%

\fancyhead{}
\fancyfoot{}

\lhead{Pre-migration Report}
%\rhead{\today}

\cfoot{\thepage}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\endinput
