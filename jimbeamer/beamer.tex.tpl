%% Beamer template for jimbeamer.
%%
%% The variables below are filled in from the YAML metadata block at the top
%% of the Markdown source, or from -V.  string.Template has no
%% conditionals, so build_variables() guarantees every variable below has a
%% value, falling back to a sane default when the metadata is silent.

\documentclass[$classoptions]{beamer}

\mode<presentation>
{
    % metadata: theme, colortheme, fonttheme
    % themes worth a try: Boadilla, CambridgeUS, Madrid
    % colour themes: dolphin, seahorse
    \usetheme{$theme}
    \usecolortheme{$colortheme}
    \usefonttheme{$fonttheme}
    %\setbeamercovered{transparent}
}

\setbeamertemplate{itemize item}[square]
\setbeamertemplate{itemize subitem}[triangle]
\setbeamertemplate{itemize subsubitem}[circle]
\setbeamertemplate{section in toc}[square]
\setbeamertemplate{navigation symbols}{}

%% An enumerate's label, in the square the themes call "projected": the
%% name is the beamer font and colour to set it in, which is what tells the
%% levels apart.
%%
%% This is beamer's own [square] template with the width measured from the
%% label rather than fixed at 2.25ex.  Fixed, it has room for one character:
%% a list ten items long printed "10" across the edges of its square, and a
%% lettered one set "(iv)" the same way.  A single character still gets the
%% same square it always did.
%% The square is beamer's, and so is this: [square] carries an [action]
%% setting 'item projected' to \scriptsize, which fired as a side effect of
%% asking for the option.  Setting the templates below by hand loses the
%% action with it, and the labels fall back to the \tiny the font theme
%% gives them -- and since the box is measured in ex of that same font, the
%% square shrinks with the digit.  This is that action, said out loud.
%% 'subitem projected' and 'subsubitem projected' inherit from it.
\setbeamerfont{item projected}{size=\scriptsize}

\newlength{\jbenumwidth}
\newcommand{\jbprojected}[2]{%
  \hbox{%
    \usebeamerfont*{#1}%
    \usebeamercolor[bg]{#1}%
    \settowidth{\jbenumwidth}{#2}%
    \addtolength{\jbenumwidth}{.9ex}%
    \ifdim\jbenumwidth<2.25ex\setlength{\jbenumwidth}{2.25ex}\fi%
    \vrule width\jbenumwidth height1.85ex depth.4ex%
    \hskip-\jbenumwidth%
    \hbox to\jbenumwidth{\hfil\color{fg}#2\hfil}%
  }%
}

\setbeamertemplate{enumerate item}{%
  \jbprojected{item projected}{\insertenumlabel}}
\setbeamertemplate{enumerate subitem}{%
  \jbprojected{subitem projected}{\insertsubenumlabel}}
\setbeamertemplate{enumerate subsubitem}{%
  \jbprojected{subsubitem projected}{\insertsubsubenumlabel}}

%% A list that says how to count -- '(a)', 'a)', '(iv)' -- reaches beamer as
%% the optional argument of enumerate, and beamer sets those labels with the
%% "mini template" instead of the three above, whatever they are.  The
%% themes make it a ball, so a lettered list came out in balls while the
%% numbered list beside it was in squares.
%%
%% One template serves all three levels, so it has to say which it is at.
%% \beameritemnestingprefix is the obvious answer and the wrong one: beamer
%% leaves it counting *every* list rather than the enumerates among
%% themselves, so a lettered list inside a bullet would take the second
%% level's colours while the same list written '1.' took the first -- two
%% lists at one level set differently by how the marker was written, which
%% is the mismatch this is all here to remove.  \@enumdepth is the number
%% the three templates above are chosen by.
\makeatletter
\setbeamertemplate{enumerate mini template}{%
  \ifnum\@enumdepth>2\relax
    \jbprojected{subsubitem projected}{\insertenumlabel}%
  \else\ifnum\@enumdepth>1\relax
    \jbprojected{subitem projected}{\insertenumlabel}%
  \else
    \jbprojected{item projected}{\insertenumlabel}%
  \fi\fi}
\makeatother

%% Separator slides carry the name alone. Beamer's own templates print
%% "Section 1" above it (\sectionname~\insertsectionnumber, then \vskip1em);
%% these are those templates with that line dropped, so the colours, fonts
%% and box of whatever theme is in use still apply.
\setbeamertemplate{part page}{%
  \begingroup
    \centering
    \begin{beamercolorbox}[sep=16pt,center]{part title}
      \usebeamerfont{part title}\insertpart\par
    \end{beamercolorbox}
  \endgroup
}
\setbeamertemplate{section page}{%
  \begingroup
    \centering
    \begin{beamercolorbox}[sep=12pt,center]{section title}
      \usebeamerfont{section title}\insertsection\par
    \end{beamercolorbox}
  \endgroup
}
\setbeamertemplate{subsection page}{%
  \begingroup
    \centering
    \begin{beamercolorbox}[sep=8pt,center]{subsection title}
      \usebeamerfont{subsection title}\insertsubsection\par
    \end{beamercolorbox}
  \endgroup
}

\usepackage{$fontfamily}          % metadata: fontfamily
\usepackage{color}
\usepackage{graphicx}
\usepackage{xspace}

%% Fenced code blocks become lstlisting, so the package is not optional.
%% Settings come before header-includes, so that a \lstset of your own wins.
\usepackage{listings}
%% Straight quotes in code: without this, 'B' in a listing comes out as
%% typographic quotes, which is wrong for a character literal.
\IfFileExists{upquote.sty}{\usepackage{upquote}}{}
\lstset{
  basicstyle=\ttfamily\small,
  columns=fullflexible,
  keepspaces=true,
  showstringspaces=false,
  upquote=true,
  breaklines=true,          % long lines wrap instead of running off the slide
  breakatwhitespace=false,
}

\newcommand{\ol}[1]{\textcolor{blue}{\ifmmode \text{[OL: #1]}\else [OL: #1] \fi}}

%% Emitted at the top of every tight list, i.e. one whose items are single
%% paragraphs. \providecommand so that a header-includes of your own wins.
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\newcommand{\hlbl}[1]{\textcolor{blue}{#1}}
\newcommand{\hlgr}[1]{\textcolor{olive!50!green}{#1}}
\newcommand{\hlrd}[1]{\textcolor{red}{#1}}
\newcommand{\hlorg}[1]{\textcolor{Orange}{#1}}
\newcommand{\hlgrey}[1]{\textcolor{black!50}{#1}}
\newcommand{\hldgr}[1]{\textcolor{olive!20!green}{#1}}
\newcommand{\hlvio}[1]{\textcolor[rgb]{0.7,0,0.35}{#1}}




%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\backupbegin}{
   \newcounter{finalframe}
   \setcounter{finalframe}{\value{framenumber}}
}
\newcommand{\backupend}{
   \setcounter{framenumber}{\value{finalframe}}
}

\newcommand{\xpause}[0]{\pause}
\newcommand{\pausex}[0]{\xpause}

%% metadata: handout.  Empties \xpause, and with it \pausex, so that every
%% frame is one page.  After the definitions above, since it redefines them.
$handout

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% metadata: section-titles.  A separator slide for each sectioning level,
%% empty when switched off.  Before header-includes, so that a deck defining
%% its own \AtBeginSection wins.
$sectionpages

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% metadata: header-includes.  Last in the preamble, so that whatever it
%% pulls in (\input{macros.tex}, \input{stylesheet.tex}, ...) can override
%% what is set above.
$headerincludes

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% The bracketed forms are the short versions beamer puts in the footline.
%% metadata: title, short-title, author, short-author, institute,
%%           short-institute, date, short-date
\title[$shorttitle]{$title}
%% Beamer skips the subtitle when it is empty, so this needs no condition.
\subtitle{$subtitle}
\author[$shortauthor]{$author}
\institute[$shortinstitute]{$institute}
\date[$shortdate]{$date}

\begin{document}

% Translation of some slides only: [label=current] in the frame header.
% \includeonlyframes{current}

%% Empty when the deck has no title, or sets 'titlepage: false'.
$titlepage

%% metadata: toc.  Empty unless asked for.
$toc

$slides


\backupbegin
\backupend

\end{document}
