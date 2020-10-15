library(e1071)
library(data.table)
library(getopt)

classifier = function(rfile, idb){
 load(idb)
  dat = fread(rfile);
  stat.mat = matrix(as.matrix(dat[match(select.block,as.matrix(dat$region.name)),'mbs',with=F]),nrow = 1);
  colnames(stat.mat) = select.block;

  probability = attr(predict(model, stat.mat, probability=T),'probabilities')[,'tumor'];
  predictor = ifelse(probability>cutoff,'tumor','normal');
  
  res.test = data.frame(sampleID=dat$sample.id[1],
                        probability=probability,
                        predictor=predictor);
  colnames(res.test) = c('sampleID','probability','predictor');
  
  return(res.test);
}

command_args <- matrix(c(
  "outdir", "o", "1", "character", "the output directory",
  "config", "c", "1", "character", "the panel configure file",
  "prefix", "p", "1", "character", "the prefix of output",
  "help", "h", "0", "logical", "this help"
), ncol = 5, byrow = T)
command_options <- getopt(command_args)

if (!is.null(command_options$help) || is.null(command_options$outdir) || is.null(command_options$prefix)
|| is.null(command_options$config)) {
  cat(paste(getopt(command_args, usage = T), "\n"))
  q()
}

# load parameters
prefix <- command_options$prefix
output_prefix <- paste0(command_options$outdir, "/", prefix)
result_file <- paste0(output_prefix, ".calling.result.txt")

if (!file.exists(result_file)) {
  cat("cannot find", result_file, "\n")
  q()
}

cfg <- read.table(command_options$config, sep = "=", strip.white = T, row.names = 1, stringsAsFactors = F)
idb <- cfg["reportDB", ]

class_result <- classifier(result_file, idb)

report_file <- paste0(output_prefix, ".report.txt")
write.table(class_result, report_file, row.names = F, col.names = T, quote = F, sep = "\t")

