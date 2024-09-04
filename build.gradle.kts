plugins {
    id("org.openrewrite.build.recipe-library") version "latest.release"
}

group = "org.openrewrite"
description = "Rewrite Python"

val latest = if (project.hasProperty("releasing")) {
    "latest.release"
} else {
    "latest.integration"
}

tasks.compileJava {
    options.release = 8
}

// disable all tests temporarily
tasks.withType<Test> {
    // This disables all test tasks
    isEnabled = false
}

dependencies {
    compileOnly("org.openrewrite:rewrite-test")
    implementation("org.openrewrite:rewrite-remote-java:latest.integration") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")

    testImplementation("org.openrewrite:rewrite-test")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")
}

val poetryProjectDir = file("rewrite")
val outputDir = layout.buildDirectory.dir("resources/main/META-INF")
val requirementsFile = outputDir.map { it.file("python-requirements.txt") }

tasks.register("prepareOutputDir") {
    doLast {
        outputDir.get().asFile.mkdirs()
    }
}

tasks.register<Exec>("exportPoetryRequirements") {
    dependsOn("prepareOutputDir")
    workingDir = poetryProjectDir
    commandLine("sh", "-c", "poetry export --without-hashes -o ${requirementsFile.get().asFile.absolutePath}")
    standardOutput = System.out
    errorOutput = System.err
}

tasks.register("appendOpenRewriteRequirements") {
    dependsOn("exportPoetryRequirements")
    doLast {
        val file = requirementsFile.get().asFile
        file.appendText("cbor2\n")
        file.appendText("openrewrite${generatePipVersionConstraint(project.version.toString())}\n")
        file.appendText("openrewrite-remote${generatePipVersionConstraint(getDirectDependencyVersion("org.openrewrite:rewrite-remote-java"))}\n")
    }
}

tasks.named("processResources") {
    dependsOn("appendOpenRewriteRequirements")
}

fun generatePipVersionConstraint(version: String): String {
    if (version.endsWith("-SNAPSHOT")) {
        return "<${version.replace("-SNAPSHOT", "")}"
    }
    val versionParts = version.split(".")
    if (versionParts.size != 3) {
        throw IllegalArgumentException("Invalid version format: $version")
    }

    val major = versionParts[0]
    val minor = versionParts[1].toInt()
    val patch = versionParts[2]

    val nextMinor = minor + 1

    return ">=${major}.${minor}.${patch},<${major}.${nextMinor}.0"
}

fun Task.getDirectDependencyVersion(dependencyName: String): String {
    val compileClasspathConfig = project.configurations.getByName("compileClasspath")
    var version = ""
    compileClasspathConfig.resolvedConfiguration.firstLevelModuleDependencies.forEach { dependency ->
        if ((dependency.module.id.group + ':' + dependency.module.id.name) == dependencyName) {
            version = dependency.module.id.version
        }
    }
    return version
}