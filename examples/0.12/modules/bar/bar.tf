resource "random_string" "hello" {
  length = local.single_length
}

resource "local_file" "hello" {
  filename = "${local.prefix}${path.module}/hello.txt"
  content  = random_string.hello.result
}

resource "random_string" "many" {
  count  = var.counts
  length = local.many_length
}

resource "local_file" "many" {
  count    = var.counts
  filename = "${local.prefix}${path.module}/many.${count.index}.txt"
  content  = element(random_string.many.*.result, count.index)
}

output "content" {
    value = random_string.many[*].result
}
